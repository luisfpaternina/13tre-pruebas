from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from ast import literal_eval
from pytz import timezone
from odoo import api, fields, models, _
from odoo.tools import float_round
import requests
from zeep import Client, Settings, Transport, helpers
import qrcode
import time

from odoo.exceptions import UserError, ValidationError

from odoo.addons.bits_api_connect.models.adapters.builder_file_adapter\
    import BuilderToFile

from odoo.addons.bits_api_connect.models.connections.api_connection\
    import ApiConnectionException

from odoo.addons.bits_api_connect.models.api_connection\
    import ApiConnection

from odoo.addons.bits_api_connect.models.getters_dict\
    import GettersDict

from .get_payroll_dict import GetPayrollDict

from odoo.addons.hr_payroll.models.browsable_object\
    import BrowsableObject

from odoo.addons.l10n_co_e_payroll.models.browsable_object\
    import Payslips

import base64

import logging
from io import BytesIO
_logger = logging.getLogger(__name__)


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def get_default_payment_way(self):
        paymnent_way = self.env['payment.way'].search([('code','=','1')])
        if paymnent_way:
            result = paymnent_way
        else:
            result = False
        
        return result

    check_send_approval = fields.Boolean()
    payment_method_id = fields.Many2one(
                                        'payment.method',
                                        String='Payment Method'
                                        )
    payment_way_id = fields.Many2one(
                                    'payment.way',
                                    string="Payment Way",
                                    default=get_default_payment_way
                                    )
    payment_date = fields.Date('Payment date')

    currency_company_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        related="company_id.currency_id"
        )

    cune_ref = fields.Char(
        string="CUNE",
        copy=False
    )

    payslip_related_id = fields.Many2one(
        'hr.payslip',
    )

    custom_field_line_ids = fields.One2many(
        'payslip.custom.field.line',
        'payslip_id',
    )

    hours_quantity = fields.Float(
        string="Quantity",
        compute='_compute_quantity_hours'
    )

    ep_sync = fields.Boolean(string="Sync", default=False, copy=False)
    ep_is_not_test = fields.Boolean(string="In production", default=False)

    # Api Response
    ep_transaction_id = fields.Char(string="ID Transaction", track_visibility='onchange')
    ep_is_valid = fields.Boolean(string="Valid", copy=False)
    ep_uuid = fields.Char(string="UUID", copy=False)
    ep_issue_date = fields.Date(string="Issue date", copy=False, track_visibility='onchange')
    ep_zip_key = fields.Char(string="zip key", copy=False)
    ep_status_code = fields.Char(string="Status code", copy=False, track_visibility='onchange')
    ep_status_description = fields.Char(
        string="Status description", copy=False, track_visibility='onchange')
    ep_status_message = fields.Char(string="Status message", copy=False, track_visibility='onchange')
    ep_file_name = fields.Char(string="file name", copy=False)
    ep_zip_name = fields.Char(string="Zip name", copy=False)
    ep_url_acceptance = fields.Char(string="URL acceptance", copy=False)
    ep_url_rejection = fields.Char(string="URL rejection", copy=False)
    ep_xml_bytes = fields.Boolean(copy=False)
    ep_errors_messages = fields.Text("Error messages", copy=False)
    ep_qr_data = fields.Text(string="QR data", copy=False, track_visibility='onchange')
    ep_app_resp_file_name = fields.Char(copy=False)
    ep_application_response_base64_bytes = fields.Binary(
        "Api response",
        attachment=True, copy=False)
    ep_dian_document_file_name = fields.Char(copy=False)
    ep_attached_document_base64_bytes = fields.Binary(
        "Dian validation voucher", attachment=True, copy=False)
    ep_pdf_base64_bytes = fields.Binary(
        'PDF file', attachment=True, copy=False)
    ep_zip_base64_bytes = fields.Binary(
        'ZIP file', attachment=True, copy=False)
    ep_dian_resp_file_name = fields.Char(copy=False)
    ep_dian_response_base64_bytes = fields.Binary(
        'Api response DIAN',
        attachment=True, copy=False)
    ep_cune_ref = fields.Char(
        string="CUNE",
        readonly=True,
        copy=False
    )
    ep_dian_state = fields.Char(
        string='Dian State',
    )
    line_detail_ids = fields.One2many(
        comodel_name='hr.payslip.dian.detail',
        inverse_name='payslip_id',
        string='Line Details',
    )
    line_result_ids = fields.One2many(
        comodel_name='hr.payslip.dian.result',
        inverse_name='payslip_id',
        string='Line Results',
    )
    line_total_ids = fields.One2many(
        comodel_name='hr.payslip.dian.total',
        inverse_name='payslip_id',
        string='Line Totals',
    )
    # QR image
    ep_qr_image = fields.Binary("QR Code", attachment=True, copy=False, track_visibility='onchange')
    ep_serie = fields.Char(copy=False)
    ep_payroll_datetime = fields.Datetime(
        string="Electronic Payroll datetime",
        default=fields.Datetime.now().replace(second=0),
        readonly=True,
        index=True,
        copy=False,
        states={'draft': [('readonly', False)]},
    )
    electronic_payroll_status = fields.Char(
        #compute='action_generate_file',
    )
    type_setting_note = fields.Selection(
        selection=[
            ('1','Replace'),
            ('2','Delete'),
        ],
        string='Type of setting note',
    )
    test_sep_10 = fields.Binary('Test sep 10')
    pred_number = fields.Char('Name of predecessor')
    pred_CUNE = fields.Char('CUNE of predecessor')
    rpr_date_gen =fields.Char('Send date')
    pred_date_gen = fields.Char('Date of predecessor')
    setting_note = fields.Text('Nota de ajuste', default='Esta es una nomina de ajuste')
    check_send_file_dian = fields.Boolean('Empty', default=False)


    def daysworked_holidays(self,holidays_emp):
        days_holidays = sum([x.holidays for x in holidays_emp])
        days_month = sum([x.enjoyment_current_month for x in holidays_emp])

        return days_month, days_holidays


    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee(self):
        res = super(HrPayslip, self)._onchange_employee()
        for record in self:
            days_month = 0
            if record.employee_id and record.date_from and record.date_to:
    
                holidays_emp = record.env['hr.payslip'].\
                                search([('employee_id','=',record.employee_id.id),
                                        ('date_from','>=',record.date_from),
                                        ('date_to','<=',record.date_to),
                                        ('struct_id.code','=','VAC')])
                
                if holidays_emp:
                    days_month = 0
                    for line in holidays_emp.line_ids:
                        if line.code in ['145','146']:
                            days_month += line.quantity
                    
                    total_days_worked = record._get_new_worked_days_lines().number_of_days - days_month
                    record.worked_days_line_ids[0].number_of_days = total_days_worked
                    amount_wage = record.contract_id.wage/record._get_new_worked_days_lines().number_of_days
                    record.worked_days_line_ids[0].amount = amount_wage * total_days_worked

        return res


    def get_total_holidays_fds(self,holidays_fds):
        for record in self:
            rule_fds = self.env['hr.salary.rule'].search([('code','=','3023')])
            if rule_fds and  rule_fds[0].include_holidays_fds:
                code_holidays_fds = rule_fds[0].include_holidays_fds.split(',')
                if record.struct_id.code == 'VAC':
                    for l3 in record.line_ids:
                        if l3.code in code_holidays_fds:
                            holidays_fds += l3.total
                    return holidays_fds
                else:
                    payslip_h = self.env['hr.payslip'].\
                                search([('employee_id','=',record.employee_id.id),
                                        ('date_from','>=',record.date_from),
                                        ('date_to','<=',record.date_to),
                                        ('struct_id.code',"=",'VAC')])
                    if payslip_h:
                        for l4 in payslip_h[-1].line_ids:
                            if l4.code in code_holidays_fds:
                                holidays_fds += l4.total
                        return holidays_fds
                    return 0
            else:
                return 0


    def compute_sheet(self):
        for record in self:
            if record.employee_id.contributor_type.code in ['20','40','59']:
                employees_name = []
                for employee in self.employee_id:
                    employees_name.append(employee.name)
                    
                raise UserError(
                    _('No se puede calcular una nómina para %s con este tipo de contribuyente' % (employees_name))
                )
        res = super(HrPayslip, self).compute_sheet()
        for record in self:
            basic_salary = record.env.company.basic_salary
            if record.worked_days_line_ids[0]:
                number_days = record.worked_days_line_ids[0].number_of_days
                amount = (basic_salary/30)
                if record.struct_id.code in ['17','19']:
                    for line in record.line_ids:
                        if line.salary_rule_id.code == 'SALU':
                            total = amount * abs(number_days)
                            line.amount = total
                            line.total = total * (line.rate)/100
                elif record.struct_id.code in ['18','20']:
                    for line in record.line_ids:
                        if line.salary_rule_id.code in ['SALU','ARL']:
                            total = amount * abs(number_days)
                            line.amount = total
                            line.total = total * (line.rate)/100



            constitutive_acum = 0
            non_constitutive_acum = 0
            holidays_fds = 0
            for line in record.line_ids:
                if line.salary_rule_id.code == 'ICO':
                    constitutive_acum += line.total
                elif line.salary_rule_id.code == 'INCO':
                    non_constitutive_acum += line.total

            total_holidays_fds = record.get_total_holidays_fds(holidays_fds)
            t = (total_holidays_fds + constitutive_acum + non_constitutive_acum)*0.4
            t1=0
            if t<non_constitutive_acum:
                t1 = non_constitutive_acum - t
            
            if record.struct_id.code == 'VAC':
                for l in record.line_ids:
                    if l.code == "3023":
                            ### HU6 CRITERIO 2 PUNTO 1
                        if total_holidays_fds > 4*basic_salary:
                            total_fds_holiday = total_holidays_fds*0.01
                            l.amount = total_holidays_fds
                            l.total = total_fds_holiday
                        else:
                            ### HU6 CRITERIO 3 PUNTO 1
                            l.unlink()  

            elif record.struct_id.code == 'NORM':
                    percentaje_cons = (constitutive_acum + non_constitutive_acum)*0.4
                    f1 = constitutive_acum
                    f2 = non_constitutive_acum
                    f3 = percentaje_cons
                    f4 = 0
                    if f3<f2:
                        f4= f2-f3

                    f5 = f4 + f1
                    f6 = f5*0.01
                    
                    ##CASO PARA HU5
                    for l1 in record.line_ids:
                        if f5 > 4*basic_salary:
                            if l1.code in ['3023']:
                                l1.amount = f5
                                l1.total = f6
    
                    ### HU6 CRITERIO 2 PUNTO 2
                    if total_holidays_fds > 4*basic_salary:
                        for l2 in record.line_ids:
                            #if l2.code in ['3010','3020']:     SALUD Y PENSIÓN
                            #    l2.total = constitutive_acum*0.04
                            if l2.code in ['3023']:
                                fds3 = t1 + constitutive_acum
                                l2.amount = fds3
                                l2.total = fds3*0.01

                    ### HU6 CRITERIO 3 PUNTO 2###
                    if total_holidays_fds < 4*basic_salary:
                        if (total_holidays_fds + constitutive_acum ) > 4*basic_salary:
                            for l1 in record.line_ids:
                                #if l1.code in ['3010','3020']:      SALUD Y PENSIÓN
                                #    l1.total = constitutive_acum*0.04
                                if l1.code == "3023":
                                    l1.amount = total_holidays_fds + constitutive_acum + t1
                                    l1.total = (total_holidays_fds + constitutive_acum + t1)*0.01
    
        return res


    def not_approve_payroll(self):
        for record in self:
            record.check_send_approval = False
        return super(HrPayslip, self).not_approve_payroll()

    def action_payslip_draft(self):
        for record in self:
            record.check_send_approval = False
        res = super(HrPayslip, self).action_payslip_draft()
        return res

    def _get_active_tech_provider(self):
        company_id = self.env.company
        if not company_id.provider_id:
            raise UserError(
                _('Please configure technology provider for electronic payroll')
            )
        return company_id.provider_id

    def _get_base_local_dict(self):
        res = super()._get_base_local_dict()
        return res

    def _generate_file(self):
        employee = self.employee_id
        contract = self.contract_id
        localdict = {
            **self._get_base_local_dict(),
            **{
                'payslip': Payslips(employee.id, self, self.env),
                'company': self.company_id.partner_id,
                'partner': BrowsableObject(
                    employee.id,
                    self.employee_id.address_home_id,
                    self.employee_id.address_home_id.env),
                'employee': employee,
                'contract': contract
            }
        }

        provider = self._get_active_tech_provider()
        if not provider:
            raise UserError(
                _('Please configure technology provider '
                  'for electronic payroll')
            )

        # CHECK REQUIRED LINES
        req_tp_lines = self.env['l10n_co.tech.provider.line'].search(
            [('cardinality', 'in', ['1_1', '1_n'])]
        )
        if self.pred_CUNE:
            req_tp_lines += self.env['l10n_co.tech.provider.line'].search(
                [('cardinality', 'in', ['setting'])]
            )

        # CHECK QUANTITY OF PAYSLIPS
        if 'payslip_count' in localdict:
            localdict['payslip_count'] += 1
        else:
            localdict['payslip_count'] = 1

        data = (
            GetPayrollDict.generate_dict_api_service(
                provider,
                req_tp_lines,
                localdict
            )
        )
        file = BuilderToFile.prepare_file_for_submission(
            provider.file_extension,
            provider.file_adapter, data,
            provider.file_separator
        )
        return file

    def _compute_quantity_hours(self):
        for record in self:
            if record.line_ids:
                new_field = \
                    [
                        line.quantity for line in record.line_ids 
                        if(
                            line.category_id.code == 'BASIC' or 
                            line.salary_rule_id.code == 'RBASIC'
                        )
                    ]
                record.hours_quantity = new_field[0] if new_field else False
            else:
                record.hours_quantity = False

    def clean_info_test(self):
        for record in self:
            record.ep_dian_state = 'Pendiente'
            record.ep_status_description = 'Pendientes'
            record.ep_status_message = 'Pendientes'
            record.ep_cune_ref = False
            record.ep_qr_data = False
            record.ep_qr_image = False
            record.unlink_response_lines_dian()

    def cron_dian_state_payslip(self):
        payslip_ids = self.env['hr.payslip'].search([
            ('ep_dian_state','in',('Pendiente',)),
        ])
        for payslip_id in payslip_ids:
            payslip_id.get_state_dian_payslip()
    
    def _get_number_dian(self):
        if not self.number:
            return False
        dict_number = self.number.split('-')
        return dict_number[0] + dict_number[1]
    
    def get_detail_payslip(self):
        for record in self:
            if not self.ep_transaction_id:
                return
            provider = self._get_active_tech_provider()
            api_conection = self._create_api_conection(provider=provider)
            number = self._get_number_dian()
            res = api_conection.download(idTransaccion=self.ep_transaction_id, numbers=number)
            if not res[2]:
                detail_vals = {
                    'request_date': datetime.now(),
                    'code': res[1]['code'],
                    'description': res[1]['description'],
                    'payslip_id': record.id,
                    'payslip_run_id': record.payslip_run_id.id,
                }
                record.ep_status_code = res[1]['code'] + ' | ' + res[1]['description']
                detail_id = self.env['hr.payslip.dian.detail'].create(detail_vals)
                if res[1]['details_payslip'] and res[1]['details_payslip'].get('DetalleNomina', False):
                    for result in res[1]['details_payslip']['DetalleNomina']:
                        if record._get_number_dian() == result.get('numero', ''):
                            record.ep_dian_state = result['estatus']

                        time.sleep(6)
                        line_vals = {
                            'number': result.get('numero', ''),
                            'status': result.get('estatus', ''),
                            'app_response': result.get('appResponse', ''),
                            'xml_signed': result.get('xmlFirmado', ''),
                            'detail_id': detail_id.id,
                            'payslip_pdf': result.get('pdfNomina', ''),
                        }
                        self.env['hr.payslip.dian.detail.line'].create(line_vals)
                        if result.get('pdfNomina', ''):
                            self.ep_file_name = record.ep_transaction_id
                            self.ep_pdf_base64_bytes = result.get('pdfNomina', '')
                            self.message_post(body=_('Archivo PDF con la informacion requerida '
                                                'para la nómina electrónica'),
                                                attachments=[(record.ep_transaction_id + '.pdf',
                                                result.get('pdfNomina', ''))
                                                ]
                                                )
    
                if (
                    record.struct_id.type_id.name == 'Liquidación' and 
                    record.ep_dian_state == 'Aceptado'
                ):
                    record.contract_id.write({
                        'date_end': record.date_to,
                        'state': 'cancel',
                    })
                    record.employee_id.write({
                        'active': False,
                    })


    def get_results_payslip(self):
        for record in self:
            if not record.ep_transaction_id:
                return
            provider = self._get_active_tech_provider()
            api_conection = self._create_api_conection(provider=provider)
            for type in ['A','E','R']:
                res = api_conection.download_results(idTransaccion=self.ep_transaction_id, type=type)
                if not res[2] and res[1]['qty'] != '0':
                    result_vals = {
                        'request_date': datetime.now(),
                        'code': res[1]['code'],
                        'description': res[1]['description'],
                        'type': res[1]['type'],
                        'qty': res[1]['qty'],
                        'payslip_id': record.id,
                    }
                    result_id = self.env['hr.payslip.dian.result'].create(result_vals)
                    if res[1]['results_payslip'] and res[1]['results_payslip'].get('ResultadoNomina', False):
                        for result in res[1]['results_payslip']['ResultadoNomina']:
                            if record._get_number_dian() == result.get('Numero', ''):
                                record.ep_status_description = res[1]['type']
                                record.ep_cune_ref = result['cune'] or False
                            line_vals = {
                                'number': result.get('Numero',''),
                                'position': result.get('posicion', ''),
                                'cune': result.get('cune',''),
                                'result': result.get('resultado',''),
                                'result_id': result_id.id,
                            }
                            if record._get_number_dian() == result.get('Numero',''):
                                record.ep_status_message = result.get('resultado','')
                                record.cune = result.get('cune','')
                            self.env['hr.payslip.dian.result.line'].create(line_vals)
    
    def get_totals_payslip(self):
        for record in self:
            if not record.ep_transaction_id:
                return
            provider = self._get_active_tech_provider()
            api_conection = self._create_api_conection(provider=provider)
            res = api_conection.download_totals(idTransaccion=self.ep_transaction_id)
            if not res[2]:
                total_vals = {
                    'request_date': datetime.now(),
                    'code': res[1]['code'],
                    'description': res[1]['description'],
                    'payslip_id': record.id,
                }
                total_id = self.env['hr.payslip.dian.total'].create(total_vals)
                if res[1]['totals_payslip']:
                    line_vals = {
                        'receipts_payslip_status': res[1]['totals_payslip'].get('RecibosNominasStatus', ''),
                        'status_payslip': res[1]['totals_payslip'].get('statusNomina', ''),
                        'pasylip_qty': res[1]['totals_payslip'].get('cantidadNomina', ''),
                        'total_id': total_id.id,
                    }
                    self.env['hr.payslip.dian.total.line'].create(line_vals)

    def get_state_dian_payslip(self):
        for record in self:
            record.ep_issue_date = date.today()
            record.get_detail_payslip()
            record.get_results_payslip()
            record.get_totals_payslip()
            if record.ep_cune_ref:
                record.ep_qr_data = 'https://catalogo-vpfe.dian.gov.co/document/searchqr?documentkey={cune}'.format(cune=record.ep_cune_ref)
                record.generate_qr_code()
            else:
                record.ep_qr_data = False
                record.ep_qr_image = False
            filename = self.number or ""
            record.message_post(
                    body=_('CUNE: %s<br/>Dian State: %s<br/>Transaction ID: %s<br/>'
                           'Description: %s<br/>') %
                          (record.ep_cune_ref or ' ', record.ep_dian_state or ' ', record.ep_transaction_id or ' ', record.ep_status_description or ' '))
    
    def generate_qr_code(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=2,
            border=2,
        )
        qr.add_data(self.ep_qr_data)
        qr.make(fit=True)
        img = qr.make_image()
        temp = BytesIO()
        img.save(temp, format="PNG")
        qr_image = base64.b64encode(temp.getvalue())
        self.ep_qr_image = qr_image

    def unlink_response_lines_dian(self):
        for record in self:
            record.line_detail_ids.unlink()
            record.line_result_ids.unlink()
            record.line_total_ids.unlink()

    def action_generate_file(self):
        self.ensure_one()
        format = '%Y-%m-%d'
        self.rpr_date_gen = Payslips._generate_date(self,format=format)
        print(self.rpr_date_gen)
        self._compute_quantity_hours()
        file = self._generate_file()
        filename = self.number or ""
        self.message_post(
            body=_('TXT file with the information required '
                   'for the electronic payroll'),
            attachments=[(filename + '.txt', file)]
        )
        #HERE WE ENCODE THE FILE TO BASE64
        file = base64.b64encode(file)
        attachments = [(filename + '.txt', file)]
        self.connectionservice()
        provider = self._get_active_tech_provider()
        request = self._create_api_conection(provider=provider)
        #print(re)
        response = request.upload(
                    'Nomina', filename, file, attachments
                )
        print(response)
        zeep_object = request.get_zeep_object(
                    'Nomina', file, attachments
                )
        print(zeep_object)
        self.message_post(body=_('El estado de la nomina por parte del proveedor tecnologico es: %s.') %
                               response['status'])
        self._generate_electronic_payslip_tech_provider(attachments)
        self.facturaxion_catch_erros_payroll(zeep_object)
        if zeep_object:
            self.ep_transaction_id = zeep_object.transaccionID
            if self.ep_transaction_id and self.line_result_ids:
                for line in self.line_result_ids:
                    self.message_post(body=_('El estado de la nomina por parte de la DIAN es: %s.') %
                               line[0].type)
                    #if line[0].type == 'Aceptadas':
                        #self.check_send_file_dian = True
        if response != False:
            self.electronic_payroll_status = response['status']
        else:
            self.electronic_payroll_status = False
        time.sleep(6)
        self.get_state_dian_payslip()
        #self.check_send_file_dian = True

    def get_sequence_data(self):
        next_number = self.env['ir.sequence'].next_by_code('salary.slip')
        print(next_number)
        return next_number
    
    def _calculate_electronic_payroll_status(self):
        self.ensure_one()
        self._compute_quantity_hours()
        file = self._generate_file()
        filename = self.number or ""
        #HERE WE ENCODE THE FILE TO BASE64
        file = base64.b64encode(file)
        attachments = [(filename + '.txt', file)]
        provider = self._get_active_tech_provider()
        request = self._create_api_conection(provider=provider)
        zeep_object = request.get_zeep_object(
                    'Nomina', file, attachments
                )
        #self._generate_electronic_payslip_tech_provider(attachments)
        #self.facturaxion_catch_erros_payroll(zeep_object)
        if zeep_object:
            self.ep_transaction_id = zeep_object.transaccionID
            if self.ep_transaction_id and self.line_result_ids:
                for line in self.line_result_ids:
                    self.message_post(body=_('El estado de la nomina por parte de la DIAN es: %s.') %
                               line[0].type)
        return
    
    #TEST SEP 10 This have to be deleted

    def action_generate_file_2(self):
        self.ensure_one()
        file = self.test_sep_10
        filename = self.number or ""
        self.message_post(
            body=_('TXT file with the information required '
                   'for the electronic payroll'),
            attachments=[(filename + '.txt', file)]
        )
        #HERE WE ENCODE THE FILE TO BASE64
        attachments = [(filename + '.txt', file)]
        self.connectionservice()
        provider = self._get_active_tech_provider()
        request = self._create_api_conection(provider=provider)
        response = request.upload(
                    'Nomina', filename, file, attachments
                )
        zeep_object = request.get_zeep_object(
                    'Nomina', file, attachments
                )
        self.message_post(body=_('El estado de la nomina por parte del proveedor tecnologico es: %s.') %
                               response['status'])
        self._generate_electronic_payslip_tech_provider(attachments)
        #self.facturaxion_catch_erros_payroll(zeep_object)
        if zeep_object:
            self.ep_transaction_id = zeep_object.transaccionID
            if self.ep_transaction_id and self.line_result_ids:
                for line in self.line_result_ids:
                    self.message_post(body=_('El estado de la nomina por parte de la DIAN es: %s.') %
                               line[0].type)
        if response != False:
            self.electronic_payroll_status = response['status']
        else:
            self.electronic_payroll_status = False

    def facturaxion_catch_erros_payroll(self, zeep_object):
        #for record in self:
            if zeep_object:
                if zeep_object['codigo'] == '01':
                    _logger.error(zeep_object['Errores'])
                    return
                elif zeep_object['codigo'] == '03':
                    _logger.error(zeep_object['Errores'])
                    raise UserError(_(
                        'The document has been rejected by tech provider. For  %s %s' % (zeep_object['Errores']['detalleError'][0]['segmento'], zeep_object['Errores']['detalleError'][0]['descripcionError'])))
                else:
                    #print(type(zeep_object['Errores']))
                    _logger.error(zeep_object['Errores'])
                    raise UserError(_(
                        'The document has been rejected by tech provider. For  %s %s' % (zeep_object['Errores']['detalleError'][0]['segmento'], zeep_object['Errores']['detalleError'][0]['descripcionError'])))
                   
    def copy(self, default={}):
        print('The function is passing for here')
        print(self)
        print(default) 
        res = super(HrPayslip, self).copy(default=default)
        return res
    
    """def create(self, default={}):
        print('The function is passing for here')
        print(self)
        print(default) 
        res = super(HrPayslip, self).create(vals)
        return re"""
    
    def copy_payslip(self):
        print(self.line_ids)
        new_object = self.copy()
        new_object['general_state'] = 'not sent'
        new_object['pred_number'] = self.number
        new_object['pred_date_gen'] = self.rpr_date_gen
        new_object['pred_CUNE'] = self.ep_cune_ref
        new_object['name'] = 'Ajuste individual del ' + self.name
        for line in self.line_ids:
            line_id = line.copy()
            line_id.write({'slip_id': new_object.id})
        #new_object['number'] = self.structure_id.
        new_object['state'] = 'verify'
        new_object['number'] = self.get_sequence_data()
        print('This is setting payroll one')
        print(new_object)
        print(self.number)
        print(new_object['pred_number'])
        print(new_object['pred_date_gen'])
        print(new_object['pred_CUNE'])
        return {
            'name': 'Test Copy',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payslip',
            'view_mode': 'form',
            'res_id': new_object.id,
        }


    def send_setting_note(self):
        self.copy()
        #for payslip in self:
            #copied_payslip = payslip.copy({'credit_note': True, 'name': _('Refund: ') + payslip.name})
           # _logger.error(copied_payslip.name)
        #for record in self:
        #for val in vals:
            #name = vals.get('name')
            #_logger.error(vals[0])
            #_logger.error(name)
            #print(vals)
        print('hello')
        
    
    def _generate_electronic_payslip_tech_provider(self, attachments):
        provider = self._get_active_tech_provider()
        for payslip in self:
            try:
                request = self._create_api_conection(provider=provider)
                filename = 'archivo_enviado_pt.txt'
                file = self._generate_file()
                # here we encode the to a base64
                file = base64.b64encode(file)
            except requests.exceptions.ConnectionError as e:
                raise ValidationError(
                    _(e))
            #here we have to add the type of document
            try:
                response = request.upload(
                    'Nomina', filename, file, attachments
                )
            except ApiConnectionException as e:
                raise ValidationError(
                    _(e))
            else:
                descripcion = response['descripcion'] \
                    if response.get('descripcion', False) else ''
                error_msg = response.get('error_msg', '')
                status = response.get('status', '')
                if status != 'accepted':
                    #raise ValidationError(_('hello other person other time'))
                    #self.l10n_co_log_rejected_invoice(
                        #error_msg, filename, file)
                    _logger.error(status)
        return
                      
    def l10n_co_log_rejected_invoice(self, descripcion, filename, file):
        if not self._context.get('not_auto_commit', False):
            self.env.cr.rollback()
        descripcion = descripcion if isinstance(descripcion, str) else ""
        with self.pool.cursor() as cr:
            self.with_env(self.env(cr=cr, user=SUPERUSER_ID)).message_post(
                body=_('Connection error:<br/>%s') % descripcion,
                attachments=[(filename, file)])
            self.with_env(self.env(cr=cr, user=SUPERUSER_ID)).write({
                'invoice_status': 'rejected'})
        raise UserError(_(
            'The document has been rejected by DIAN. For '
            'more information, please contact the '
            'administrator.\nError: %s' % (descripcion.replace("<br/>", "\n"))
        ))        

    def l10n_co_log_rejected_invoice_connection(self, e):
        if not self._context.get('not_auto_commit', False):
            self.env.cr.rollback()
        with self.pool.cursor() as cr:
            self.with_env(self.env(cr=cr, user=SUPERUSER_ID)).message_post(
                body=_('Connection error:<br/>%s') % e)
            self.with_env(self.env(cr=cr, user=SUPERUSER_ID)).write({
                'invoice_status': 'rejected'})
        raise UserError(_(
            'The connection is down '
            'more information, please contact the '
            'administrator.\nError: %s' % e
        ))

        """for invoice in self:
            try:
                request = self._create_api_conection(provider=provider)
                filename = 'archivo_enviado_pt.txt'
                file = invoice._generate_file()
            except requests.exceptions.ConnectionError as e:
                invoice.l10n_co_log_rejected_invoice_connection(e)
            try:
                response = request.upload(
                    invoice._get_ei_type_dian(), filename, file, attachments
                )
            except ApiConnectionException as e:
                invoice.l10n_co_log_rejected_invoice(e, filename, file)
            else:
                descripcion = response['descripcion'] \
                    if response.get('descripcion', False) else ''
                error_msg = response.get('error_msg', '')
                status = response.get('status', '')
                if status != 'accepted':
                    invoice.l10n_co_log_rejected_invoice(
                        error_msg, filename, file)
                cufe = response['cufe'] if response.get('cufe', False) else ''
                transaccionID = response['transaccionID'] \
                    if response.get('transaccionID', False) else ''
                numeroDocumento = response['numeroDocumento'] \
                    if response.get('numeroDocumento', False) else ''
                cadenaQR = response['cadenaQR'] \
                    if response.get('cadenaQR', False) else ''
                invoice.message_post(
                    body=_('CUDE/CUFE: %s<br/>Transaction No: %s<br/>'
                           'No Document: %s<br/>Description: %s<br/>') %
                          (cufe, transaccionID, numeroDocumento, descripcion),
                    attachments=[(filename, file)])
                invoice.cufe_cude_ref = cufe
                invoice.invoice_status = status
                invoice.ei_number = transaccionID
                invoice.ei_qr_data = cadenaQR
                invoice.generate_qr_code()"""
    
    def update_tz(self, date_now):
        dt_format = "%d-%m-%Y %H:%M:%S"
        tz = self.env.user.tz
        date_user_tz = date_now.astimezone(timezone(tz))
        date_user_tz = date_user_tz.strftime(dt_format)

        return date_user_tz

    @api.model
    def _create_api_conection(self, provider=None, url=None):
        tech_provider = (
            self._get_active_tech_provider()
                if not provider else provider
        )
        if not url:
            url = provider.url_upload or ''
        result = ApiConnection.prepare_connection(tech_provider,url)
        print('this is the result of api conection')
        print(result)
        return result

    def connectionservice(self):
        username = "USR_WS_FAX004"
        password = "FAX004"
        company = "FAX"
        url_connection = "http://169.60.157.172:8093/Services/NominaServices.asmx?wsdl"
        transport = Transport(timeout=60)
        settings = Settings(strict=False, xml_huge_tree=True)
        client_service = Client(url_connection,
                            settings=settings, transport=transport)
        object_methods = [method_name for method_name in dir(client_service.service)]
        exe_method = client_service.service.EmitirNomina()
        response = helpers.serialize_object(exe_method, dict)

    def get_detail_for_massive_payslip(self,api_conection):
        for record in self:
            if not record.ep_transaction_id:
                return
            number = record._get_number_dian()
            res = api_conection.download(
                idTransaccion=self.ep_transaction_id, numbers=number
            )
            if not res[2]:

                detail_vals = {
                    'request_date': datetime.now(),
                    'code': res[1]['code'],
                    'description': res[1]['description'],
                    'payslip_id': record.id,
                    'payslip_run_id': record.payslip_run_id.id,
                }
                record.ep_status_code = (
                    res[1]['code'] + ' | ' + res[1]['description']
                )
                detail_id = (
                    self.env['hr.payslip.dian.detail'].create(detail_vals)
                )

                if (
                    res[1]['details_payslip'] and 
                    res[1]['details_payslip'].get('DetalleNomina', False)
                ):
                    for result in res[1]['details_payslip']['DetalleNomina']:
                        if number == result.get('numero', ''):
                            record.ep_dian_state = result['estatus']

                        line_vals = {
                            'number': result.get('numero', ''),
                            'status': result.get('estatus', ''),
                            'app_response': result.get('appResponse', ''),
                            'xml_signed': result.get('xmlFirmado', ''),
                            'detail_id': detail_id.id,
                            'payslip_pdf': result.get('pdfNomina', ''),
                        }
                        self.env['hr.payslip.dian.detail.line'].create(
                            line_vals
                        )
                        if result.get('pdfNomina', ''):
                            self.ep_file_name = record.ep_transaction_id
                            self.ep_pdf_base64_bytes = (
                                result.get('pdfNomina', '')
                            )
                            self.message_post(
                                body =_(
                                    'Archivo PDF con la informacion requerida '
                                    'para la nómina electrónica'
                                ),
                                attachments=[(
                                    record.ep_transaction_id + '.pdf',
                                    result.get('pdfNomina', '')
                                )]
                            )

                if (
                    record.struct_id.type_id.name == 'Liquidación' and 
                    record.ep_dian_state == 'Aceptado'
                ):
                    record.contract_id.write({
                        'date_end': record.date_to,
                        'state': 'cancel',
                    })
                    record.employee_id.write({
                        'active': False,
                    })