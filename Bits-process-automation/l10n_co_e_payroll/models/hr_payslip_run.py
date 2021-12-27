import time
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from ast import literal_eval
from odoo import api, fields, models, _
from odoo.tools import float_round
from odoo.exceptions import UserError, ValidationError
import openerp.addons.decimal_precision as dp

from odoo.addons.bits_api_connect.models.connections.api_connection\
    import ApiConnectionException
from odoo.addons.l10n_co_e_payroll.models.browsable_object import Payslips
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject
from .get_payroll_dict import GetPayrollDict
from odoo.addons.bits_api_connect.models.api_connection import ApiConnection
from odoo.addons.bits_api_connect.models.adapters.builder_file_adapter\
    import BuilderToFile

from collections import Counter
from base64 import b64encode
import requests
import logging
_logger = logging.getLogger(__name__)

VPFE = "https://catalogo-vpfe.dian.gov.co/document/searchqr?documentkey={cune}"

class HrPayslipRunInherit(models.Model):
    _name = 'hr.payslip.run'
    _inherit = [
        'hr.payslip.run', 
        'mail.thread', 
        'portal.mixin',
    ]

    # Determine if there is any rejected payslip
    def _get_payslips_rejected(self):
        for record in self:
            record.payslip_rejected = False
            for payslip in record.slip_ids:
                if payslip.ep_dian_state == 'Rechazado':
                    record.payslip_rejected = True
                    break
                    

    payment_method_id = fields.Many2one(
                                        'payment.method',
                                        String='Payment Method'
                                        )
    payment_way_id = fields.Many2one(
                                    'payment.way',
                                    string="Payment Way"
                                    )
    payment_date = fields.Date('Payment date')
    # DIAN Response Relations and State
    dian_state = fields.Selection(
        selection=[
            ('rejected','Rejected'),
            ('wait','Wait'),
            ('done','Done'),
        ],
        string='Dian State',
    )
    line_detail_ids = fields.One2many(
        comodel_name='hr.payslip.dian.detail',
        inverse_name='payslip_run_id',
        string='Line Details',
    )
    line_result_ids = fields.One2many(
        comodel_name='hr.payslip.dian.result',
        inverse_name='payslip_run_id',
        string='Line Results',
    )
    line_total_ids = fields.One2many(
        comodel_name='hr.payslip.dian.total',
        inverse_name='payslip_run_id',
        string='Line Totals',
    )
    dian_file_generated = fields.Boolean(string='File Generated', copy=False)
    dian_file_sended = fields.Boolean(string='File Sended')
    payslip_rejected = fields.Boolean(
        string='Payslips Rejected',
        compute='_get_payslips_rejected',
    )
    # Api DIAN Response
    ep_transaction_id = fields.Char(string="ID Transaction", copy=False)
    ep_issue_date = fields.Date(string="Issue date", copy=False)
    ep_status_code = fields.Char(string="Status code", copy=False)
    ep_status_description = fields.Char(
        string="Status description", copy=False)
    ep_status_message = fields.Char(string="Status message", copy=False)
    ep_transaction_id_history = fields.Char(
        string="Transaction ID History", 
        copy=False)

    # Get number of payslip in DIAN format
    #
    # return String with payslip number
    def get_payslip_number_dian(self, slip):
        dict_number = slip.number.split('-')
        return dict_number[0] + dict_number[1]

    # Get payslip related with the payslip run
    #
    # return: List of payslip or an empty list
    def get_payslips_related(self):
        for record in self:
            payslip_ids = []
            if self.env.context.get('only_rejected'):
                for payslip in record.slip_ids:
                    if payslip.state != 'done':
                        continue
                    if payslip.ep_dian_state == 'Rechazado':
                        payslip_ids.append(payslip)
            else:
                payslip_ids = [
                    x for x in record.slip_ids if x.state == 'done'
                ]
            return payslip_ids

    # Collects information from rules of each payslip related
    #
    # return: data from payslips (or empty list) and provider (or False)
    def get_payslips_data(self):
        for record in self:
            
            data_list = []
            provider = False

            payslip_ids = record.get_payslips_related()

            payslip_count = len(payslip_ids)
            exc_msg = ""

            for payslip in payslip_ids:
                try:
                    employee = payslip.employee_id
                    contract = payslip.contract_id
                    localdict = {
                        **payslip._get_base_local_dict(),
                        **{
                            'payslip': Payslips(employee.id, payslip, payslip.env),
                            'company': payslip.company_id.partner_id,
                            'partner': BrowsableObject(
                                employee.id,
                                payslip.employee_id.address_home_id,
                                payslip.employee_id.address_home_id.env),
                            'employee': employee,
                            'contract': contract
                        }
                    }

                    provider = payslip._get_active_tech_provider()

                    # CHECK REQUIRED LINES
                    req_tp_lines = self.env['l10n_co.tech.provider.line'].search(
                        [('cardinality', 'in', ['1_1', '1_n'])]
                    )

                    # CHECK QUANTITY OF PAYSLIPS
                    localdict['payslip_count'] = payslip_count
                    
                    # Add payslip data to global data
                    data_list += [(
                        GetPayrollDict.generate_dict_api_service(
                            provider,
                            req_tp_lines,
                            localdict
                        )
                    )]
                except Exception as e:
                    if exc_msg:
                        exc_msg += "\n"
                    
                    exc_msg += e.name + " - " + payslip.number
                    payslip_count -= 1
                    continue
            
            if exc_msg:
                raise ValidationError(exc_msg)

            return data_list, provider

    # Generate massive payslip number from tries number and redord id
    #
    # return number of massive payslip (string)
    def get_mass_file_number(self):
        for record in self:
            number = "idmass" + str(record.id)
            return number
    
    # Sort data list and generate mass electronic payslip file
    #
    # return: File with payslips related
    def sort_payslips_data(self):
        for record in self:

            data = []

            data_list, provider = record.get_payslips_data()

            # Validation to know if is required delete header and footer
            if len(data_list) > 1:
                count_record = 1
                for payslip_data in data_list:
                    
                    # Remove header
                    if count_record > 1:
                        payslip_data.pop(0)
                    else:
                        for line in payslip_data[0]['lines']:
                            if line['label'] == 'idNomina':
                                line['value'] = record.get_mass_file_number()

                    # Remove footer
                    if count_record < len(data_list):
                        payslip_data.pop(len(payslip_data) - 1)
                    
                    data += payslip_data
                    count_record += 1
            else:
                data = data_list[0]

            mass_ep_file = BuilderToFile.prepare_file_for_submission(
                provider.file_extension,
                provider.file_adapter, data,
                provider.file_separator
            )

            return mass_ep_file

    # Generate the file to massive Electronic Payroll process
    # and save the file in the attachments
    #
    # return list with filename and file
    def generate_epayroll_file(self):
        for record in self:

            if record.get_payslips_related():

                mass_file = record.sort_payslips_data()

                if mass_file:
                    
                    att_msg = ""

                    if self.env.context.get('send_action'):
                        att_msg = _('TXT file with the information required '
                            'for the electronic payroll - Sended')
                    else:
                        att_msg = _('TXT file with the information required '
                            'for the electronic payroll - Generated')

                    filename = record.name or ""
                    record.message_post(
                        body=att_msg,
                        attachments=[(filename + '.txt', mass_file)]
                    )
                    attachments = [(filename + '.txt', mass_file)]

                    record.dian_file_generated = True

                    return attachments

                else:

                    raise ValidationError(_("""The file has not 
                    been generated."""))

            else:
                raise ValidationError(_("""The payslip run haven't any 
                payslip related."""))

    # Get the active tech provider in the company
    #
    # return provider object
    def _get_active_tech_provider(self):
        company_id = self.env.company
        return company_id.provider_id or False

    # Get request for connect with tech provider
    #
    # return connection with the server
    @api.model
    def _create_api_connection(self, provider, url=None):
        if not url and provider:
            url = provider.url_upload or ''
        
        result = ApiConnection.prepare_connection(provider,url)
        return result

    # Generate file and send to tech provider
    def _generate_electronic_payslip_tech_provider(self):

        for record in self:
            
            # Get attachments to send
            attachments = record.generate_epayroll_file()

            # Get active tech provider
            provider = record._get_active_tech_provider()

            try:
                request = record._create_api_connection(provider=provider)
                filename = attachments[0][0]
                file = attachments[0][1]

            except requests.exceptions.ConnectionError as e:
                raise ValidationError(_(e))
            try:
                encode_file = b64encode(file)
                response = request.upload(
                    'Nomina Masiva', filename, encode_file, attachments
                )
            except ApiConnectionException as e:
                raise ValidationError(_(e))
            else:
                descripcion = response['descripcion'] \
                    if response.get('descripcion', False) else ''
                error_msg = response.get('error_msg', '')
                status = response.get('status', '')
                if status != 'accepted':
                    error_msg = ""
                    errors = response['input_dict']['Errores']['detalleError']
                    for error in errors:
                        if error_msg:
                            error_msg += "\n\n"
                        error_msg += "Error en segmento: " + error['segmento']
                        error_msg += "\nError: " + error['descripcionError']
                    raise ValidationError(error_msg)
            return response

    # Update the transaction ID field in each of the payslips
    def update_dian_transaction_id(self, transaction_id):
        for record in self:

            if record.ep_transaction_id_history:
                trans_history = record.ep_transaction_id_history + ", "
            else:
                trans_history = ""

            record.write({
                'ep_transaction_id': transaction_id,
                'ep_transaction_id_history': trans_history + transaction_id
            })

            payslip_ids = record.get_payslips_related()

            for payslip in payslip_ids:
                payslip.write({
                    'ep_transaction_id': transaction_id
                })

    # Send massive payslip file through Facturaxion service
    def send_massive_file(self):
        for record in self:

            record = record.with_context(send_action=True)
            response = record._generate_electronic_payslip_tech_provider()
            end_message = "Estado del proveedor tecnologico: Aprobado"
            end_message += " - " + response['descripcion']

            record.message_post(body=end_message,)

            if (
                'input_dict' in response and 
                'transaccionID' in response['input_dict']
            ):
                transaction_id = response['input_dict']['transaccionID']
                record.update_dian_transaction_id(transaction_id)           
                time.sleep(60)
                record.get_state_dian_massive_payslip()

    # Get results of payslips
    #
    # return a dictionary with result types values
    def get_result_massive_payslip(self, provider, api_connection):
        for record in self:

            if not record.ep_transaction_id:
                return False, False

            # Required classes for the function
            ps_dian_result = self.env['hr.payslip.dian.result']
            ps_dian_result_line = self.env['hr.payslip.dian.result.line']

            # Dictionary with results for each type of result
            result_dicts = {}

            for res_type in ['A','E','R']:
                res = api_connection.download_results(
                    idTransaccion=record.ep_transaction_id, 
                    type=res_type
                )
                
                result_dicts[res_type] = []
                line_vals = {}
                result_vals = {}
                
                if not res[2] and res[1]['qty'] != '0':
                    result_vals = {
                        'request_date': datetime.now(),
                        'code': res[1]['code'],
                        'description': res[1]['description'],
                        'type': res[1]['type'],
                        'qty': res[1]['qty'],
                        'payslip_run_id': record.id,
                    }
                    result_id = ps_dian_result.create(result_vals)

                    if (
                        res[1]['results_payslip'] and 
                        res[1]['results_payslip'].get('ResultadoNomina', False)
                    ):
                        # Get result of all payslips
                        res_slip = res[1]['results_payslip']['ResultadoNomina']
                        for result in res_slip:
                            line_vals = {
                                'number': result.get('Numero',''),
                                'position': result.get('posicion', ''),
                                'cune': result.get('cune',''),
                                'result': result.get('resultado',''),
                                'result_id': result_id.id,
                            }
                            # Set specific information in 
                            payslip_ids = record.get_payslips_related()

                            for payslip in payslip_ids:
                                payslip_number = (
                                    record.get_payslip_number_dian(payslip)
                                )
                                if payslip_number == result.get('Numero',''):
                                    payslip.ep_status_description = (
                                        res[1]['type']
                                    )
                                    payslip.ep_cune_ref = (
                                        result['cune'] or False
                                    )
                                    payslip.ep_status_message = (
                                        result.get('resultado','')
                                    )
                                    payslip.cune = result.get('cune','')
                                    record.ep_status_message = (
                                        result.get('resultado','')
                                    )
                                    record.cune = result.get('cune','')

                            ps_dian_result_line.create(line_vals)

                            result_dicts[res_type].append(
                                [result_vals, line_vals]
                            )

        return result_dicts

    # Update result and result lines in each payslip related
    def update_slips_results(self, result_vals):
        for record in self:

            # Required classes for the function
            ps_dian_result = self.env['hr.payslip.dian.result']
            ps_dian_result_line = self.env['hr.payslip.dian.result.line']

            # Create result and result lines for each payslip related
            if result_vals:
                for res_key in result_vals:
                    if result_vals[res_key]:
                        for res_dict in result_vals[res_key]:
                            res_vals = res_dict[0]
                            slip_number = res_dict[1]['number']
                            
                            payslip_ids = record.get_payslips_related()

                            for payslip in payslip_ids:
                                payslip_number = (
                                    record.get_payslip_number_dian(payslip)
                                )
                                if slip_number == payslip_number:
                                    res_vals['payslip_run_id'] = False
                                    res_vals['payslip_id'] = payslip.id
                                    res_vals['qty'] = 1
                                    new_result = ps_dian_result.create(
                                        res_vals
                                    )
                                    line_vals = res_dict[1]
                                    line_vals['result_id'] = new_result.id
                                    ps_dian_result_line.create(line_vals)

    # Get totals of payslips
    #
    # return dictionaries with total and total lines values
    def get_total_massive_payslip(self, provider, api_connection):
        for record in self:
            if not record.ep_transaction_id:
                return False, False

            # Required classes for the function
            ps_dian_total = self.env['hr.payslip.dian.total']
            ps_dian_total_line = self.env['hr.payslip.dian.total.line']

            # Create result and result lines for each payslip related
            res = api_connection.download_totals(
                idTransaccion=record.ep_transaction_id
            )

            total_vals = {}
            line_vals = {}

            if not res[2]:
                total_vals = {
                    'request_date': datetime.now(),
                    'code': res[1]['code'],
                    'description': res[1]['description'],
                    'payslip_run_id': record.id,
                }
                total_id = ps_dian_total.create(total_vals)
                if res[1]['totals_payslip']:
                    totals = res[1]['totals_payslip']
                    line_vals = {
                        'receipts_payslip_status': totals.get(
                            'RecibosNominasStatus', ''
                        ),
                        'status_payslip': totals.get('statusNomina', ''),
                        'pasylip_qty': totals.get('cantidadNomina', ''),
                        'total_id': total_id.id,
                    }
                    ps_dian_total_line.create(line_vals)

            return total_vals, line_vals

    # Update total and total lines in each payslip related
    def update_slips_totals(self, total_vals, total_line_vals):
        for record in self:
            
            # Required classes for the function
            ps_dian_total = self.env['hr.payslip.dian.total']
            ps_dian_total_line = self.env['hr.payslip.dian.total.line']

            # Create total and total lines for each payslip related
            if total_vals:
                payslip_ids = record.get_payslips_related()

                for payslip in payslip_ids:
                    total_vals['payslip_run_id'] = False
                    total_vals['payslip_id'] = payslip.id
                    new_total = ps_dian_total.create(total_vals)
                    if total_line_vals:
                        total_line_vals['total_id'] = new_total.id
                        ps_dian_total_line.create(total_line_vals)

    # Establish massive and individual payslip status in DIAN platform
    def _calculate_electronic_payroll_status(self):
        for record in self:
            msg = "El estado de la nomina por parte de la DIAN es:"
            status_dict = {}
            for payslip in record.get_payslips_related():
                if payslip.ep_dian_state in status_dict:
                    status_dict[payslip.ep_dian_state] += 1
                else:
                    status_dict[payslip.ep_dian_state] = 1
            
            for state in status_dict:
                msg += "\n- " + str(status_dict[state])
                if state:
                    msg += " " + state
            record.message_post(body= msg)

    # Get status of each payslips in DIAN with details and results
    #
    # get_results_payslip
    def get_state_dian_massive_payslip(self):
        for record in self:

            # Remove old responses to get a clean log
            record.unlink_massive_response_lines_dian()

            # Set consult date
            record.ep_issue_date = date.today()

            payslip_ids = record.get_payslips_related()

            for payslip in payslip_ids:
                payslip.ep_issue_date = date.today()

            # Get basic data to execute functions
            provider = record._get_active_tech_provider()
            api_connection = record._create_api_connection(provider=provider)

            # Set details, results and totals in each payslip
            for payslip in payslip_ids:
                payslip.get_detail_for_massive_payslip(api_connection)
                # Relate details for massive payslip
                if payslip.line_detail_ids:
                    for detail_line in payslip.line_detail_ids:
                        detail_line.payslip_run_id = record.id

            for detail in record.line_detail_ids:
                detail._get_general_status()

            # Get result and result lines information
            result_vals = record.get_result_massive_payslip(
                provider, 
                api_connection
            )

            # Update result and result lines in each payslip related
            record.update_slips_results(result_vals)

            # Get total and total lines information
            total_vals, total_line_vals = record.get_total_massive_payslip(
                provider, 
                api_connection
            )

            # Update total and total lines in each payslip related
            record.update_slips_totals(total_vals, total_line_vals)

            # Establish massive and individual payslip status in DIAN platform
            record._calculate_electronic_payroll_status()

            # Update payslip and payslip run fields
            status_list = []
            description_list = []
            status_msg_list = []
            
            payslip_ids = record.get_payslips_related()

            for payslip in payslip_ids:
                if payslip.ep_cune_ref:
                    payslip.ep_qr_data = VPFE.format(cune=payslip.ep_cune_ref)
                    payslip.generate_qr_code()
                if payslip.ep_status_code:
                    status_list.append(payslip.ep_status_code)
                if payslip.ep_status_description:
                    description_list.append(payslip.ep_status_description)
                if payslip.ep_status_message:
                    status_msg_list.append(payslip.ep_status_message)

            if status_list:
                status_dict = Counter(status_list)
                status_run_value = ""
                for code in status_dict:
                    if status_run_value:
                        status_run_value += " - "
                    status_run_value += (
                        code + " (" + str(status_dict[code]) + ")"
                    )
                record.ep_status_code = status_run_value
            if description_list:
                description_dict = Counter(description_list)
                description_run_value = ""
                for code in description_dict:
                    if description_run_value:
                        description_run_value += " - "
                    description_run_value += (
                        code + " (" + str(description_dict[code]) + ")"
                    )
                record.ep_status_description = description_run_value
            if status_msg_list:
                status_msg_dict = Counter(status_msg_list)
                status_msg_run_value = ""
                for code in status_msg_dict:
                    if status_msg_run_value:
                        status_msg_run_value += " - "
                    status_msg_run_value += (
                        code + " (" + str(status_msg_dict[code]) + ")"
                    )
                record.ep_status_message = status_msg_run_value

    # Unlink DIAN lines related with massive and individual payslips
    def unlink_massive_response_lines_dian(self):
        for record in self:

            payslip_ids = record.get_payslips_related()

            for payslip in payslip_ids:
                for detail in payslip.line_detail_ids:
                    detail.unlink()
                for result in payslip.line_result_ids:
                    result.unlink()
                for total in payslip.line_total_ids:
                    total.unlink()

    # Send massive payslip file with only rejected payslips
    def send_rejected_payslip_massive_file(self):
        for record in self:
            if record.payslip_rejected:  
                record = record.with_context(send_action=True,only_rejected=True)
                response = record._generate_electronic_payslip_tech_provider()
                end_message = "Estado del proveedor tecnologico: Aprobado"
                end_message += " - " + response['descripcion']

                record.message_post(body=end_message,)

                if (
                    'input_dict' in response and 
                    'transaccionID' in response['input_dict']
                ):
                    transaction_id = response['input_dict']['transaccionID']
                    record.update_dian_transaction_id(transaction_id)           
                    time.sleep(60)
                    record.get_state_dian_massive_payslip()
            else:
                raise ValidationError(_("There isn't any payslip rejected"))
