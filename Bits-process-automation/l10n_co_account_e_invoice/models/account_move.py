# coding: utf-8
import io
import xml.dom.minidom
import zipfile
import pytz
import qrcode
import requests
from functools import partial
from itertools import groupby
from odoo.tools.misc import formatLang, get_lang

from collections import defaultdict
from os import listdir

from datetime import date
from datetime import datetime, timedelta
import base64
from io import BytesIO

from odoo import api, fields, models, tools, _, SUPERUSER_ID
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_TIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.tools import float_round, date_utils

from odoo.addons.l10n_co_account_e_invoice.models.browsable_object \
    import BrowsableObject, Invoive

from odoo.addons.bits_api_connect.models.adapters.builder_file_adapter\
    import BuilderToFile

from odoo.addons.bits_api_connect.models.connections.api_connection\
    import ApiConnectionException

from odoo.addons.bits_api_connect.models.api_connection\
    import ApiConnection


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    def _get_ei_type_document_id(self):
        base = 'l10n_co_account_e_invoice.'
        _ref = base + 'l10n_co_type_documents_5' \
            if self.type == 'out_refund' \
            else base + 'l10n_co_type_documents_1'
        res = self.env.ref(_ref, raise_if_not_found=False)
        return res.id if (res and res.id) else res

    operation_type = fields.Many2one(
        'l10n_co.type_operations',
        string="Operation Type",
        default=lambda self: self.env.ref(
            'l10n_co_account_e_invoice.l10n_co_type_operations_2',
            raise_if_not_found=False),
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    payment_option_id = fields.Many2one(
        'l10n_co.payment.option',
        string="Payment Option",
        default=lambda self: self.env.ref(
            'l10n_co_account_e_invoice.l10n_co_payment_option_1',
            raise_if_not_found=False),
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    ei_type_document_id = fields.Many2one(
        'l10n_co.type_documents',
        string="Document type",
        default=_get_ei_type_document_id,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    ei_payment_form_id = fields.Many2one(
        'l10n_co.payment_forms',
        string="Forms payment",
        default=lambda self: self.env.ref(
            'l10n_co_account_e_invoice.l10n_co_payment_forms_01',
            raise_if_not_found=False),
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    cufe_cude_ref = fields.Char(
        string="CUFE/CUDE",
        readonly=True,
        copy=False
    )
    description_code_credit = fields.Many2one(
        'l10n_co.description_code',
        string="Credit Note Concept",
        copy=False,
        domain="[('type', '=', 'credit')]",
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    is_direct_payment = fields.Boolean(
        "Direct Payment from Colombia",
        compute="_compute_is_direct_payment"
    )
    description_code_debit = fields.Many2one(
        'l10n_co.description_code',
        string="Debit Note Concept",
        copy=False,
        domain="[('type', '=', 'debit')]",
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    debit_note = fields.Boolean(
        related="journal_id.debit_note",
        readonly=True
    )
    ei_origin_id = fields.Many2one(
        'account.move',
        string="Document Reference",
        domain="[('type', '=', 'out_invoice')]",
        copy=False,
        help="This is the invoice which needed correction by this \
        debit note. We have a field for credit notes, but need one \
        here for its positive counterpart.",
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    status_inquiry_deadline = fields.Datetime(
        compute="compute_query_deadline",
        store=True
    )
    invoice_status = fields.Selection([
        ('not_sent', 'Not sent'),
        ('processing', 'Processing'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')],
        string='Electronic Invoice Status',
        readonly=True, default='not_sent', copy=False)

    ei_amount_text = fields.Text(
        string="Amount with letters",
        default="")

    ei_date_currency_change = fields.Date(
        string='Date from',
        required=True,
        default=datetime.now())

    ei_number = fields.Char(string="Number", copy=False)
    ei_send = fields.Boolean(
        string="Validated",
        default=True, copy=False)
    ei_customer = fields.Text(string="customer json", copy=False)
    ei_legal_monetary_totals = fields.Text(string="legal_monetary_totals json")
    ei_invoice_lines = fields.Text(string="invoice_lines json")

    ei_sync = fields.Boolean(string="Sync", default=False, copy=False)
    ei_is_not_test = fields.Boolean(string="In production", default=False)

    # API Response:
    ei_is_valid = fields.Boolean(string="Valid", copy=False)
    ei_uuid = fields.Char(string="UUID", copy=False)
    ei_issue_date = fields.Date(string="Issue date", copy=False)
    ei_zip_key = fields.Char(string="zip key", copy=False)
    ei_status_code = fields.Char(string="Status code", copy=False)
    ei_status_description = fields.Char(
        string="Status description", copy=False)
    ei_status_message = fields.Char(string="Status message", copy=False)
    ei_file_name = fields.Char(string="file name", copy=False)
    ei_zip_name = fields.Char(string="Zip name", copy=False)
    ei_url_acceptance = fields.Char(string="URL acceptance", copy=False)
    ei_url_rejection = fields.Char(string="URL rejection", copy=False)
    ei_xml_bytes = fields.Boolean(copy=False)
    ei_errors_messages = fields.Text("Error messages", copy=False)
    ei_qr_data = fields.Text(string="QR data", copy=False)
    ei_app_resp_file_name = fields.Char(copy=False)
    ei_application_response_base64_bytes = fields.Binary(
        "Api response",
        attachment=True, copy=False)
    ei_dian_document_file_name = fields.Char(copy=False)
    ei_attached_document_base64_bytes = fields.Binary(
        "Dian validation voucher", attachment=True, copy=False)
    ei_pdf_base64_bytes = fields.Binary(
        'PDF file', attachment=True, copy=False)
    ei_zip_base64_bytes = fields.Binary(
        'ZIP file', attachment=True, copy=False)
    ei_dian_resp_file_name = fields.Char(copy=False)
    ei_dian_response_base64_bytes = fields.Binary(
        'Api response DIAN',
        attachment=True, copy=False)

    # QR image
    ei_qr_image = fields.Binary("QR Code", attachment=True, copy=False)

    ei_folio = fields.Char(string="Ei invoice", copy=False)
    ei_serie = fields.Char(copy=False)

    ei_invoice_datetime = fields.Datetime(
        string="Electronic Invoice datetime",
        default=fields.Datetime.now().replace(second=0),
        readonly=True,
        index=True,
        copy=False,
        states={'draft': [('readonly', False)]},
    )
    attachments = False

    ei_ubl_note = fields.Text("Ubl extra info", copy=False)

    advances_line_ids = fields.Many2many(
        'account.move.line',
        string='Advances Items',
    )

    extra_ref_ids = fields.Many2many(
        'account.extra.refs',
        string='Advances Items',
    )

    is_visible_deb_cred_note = fields.Boolean(
        compute="compute_debit_credit_note_visible",
        store=True,
        default=False
    )
    is_debit_note = fields.Boolean(
        compute="compute_debit_credit_note_visible",
        store=True,
        default=False
    )
    is_credit_note = fields.Boolean(
        compute="compute_debit_credit_note_visible",
        store=True,
        default=False
    )

    # Python Code
    def _get_base_local_dict(self):
        return {
            'float_round': float_round
        }

    def _get_active_tech_provider(self):
        config = self.env['ir.config_parameter'].sudo()
        _id = config.get_param('l10n_co_tech_provider.provider_id')
        return self.env['l10n_co.tech.provider'].browse(int(_id))

    def generate_dict_invoice_dian(self):

        def _generate_lines(localdict, line_ids):
            res = []
            for line in line_ids:
                if line.act_field_id and not line.act_field_id\
                   ._satisfy_condition(localdict):
                    continue
                if line.act_field_id:
                    line.act_field_id.validate_required_field(localdict)
                row = dict()
                row['head'] = line.code
                row['lines'] = []
                if line.act_field_id \
                   and line.act_field_id._compute_rule(localdict):
                    headers = line.act_field_id._compute_rule(localdict)
                    for head in headers:
                        localdict['record'] = head
                        row['lines'].append(_generate_children(
                            localdict, line.children_ids))
                else:
                    row['lines'] = _generate_children(
                        localdict, line.children_ids)
                res.append(row)
            return res

        def _generate_children(localdict, children_ids):
            lines = []
            for field_line in children_ids:
                rule = field_line.act_field_id
                if rule and not rule._satisfy_condition(localdict):
                    continue
                rule.validate_required_field(localdict)
                if field_line.children_ids:
                    row = dict()
                    row['head'] = field_line.code
                    row['lines'] = []
                    if rule and rule._compute_rule(localdict):
                        head = rule._compute_rule(localdict)
                        if not isinstance(head, list):
                            row['lines'] = _generate_children(
                                localdict, field_line.children_ids)
                            lines.append(row)
                        else:
                            for head_line in head:
                                localdict['record_1'] = head_line
                                lines.append({
                                    'head': field_line.code,
                                    'lines': _generate_children(
                                        localdict, field_line.children_ids)
                                })
                        continue
                value = ''
                rule = field_line.act_field_id
                compute_rule = rule._compute_rule(localdict)
                if compute_rule:
                    value = compute_rule
                elif not isinstance(compute_rule, bool):
                    value = compute_rule

                line_row = {
                    'label': field_line.name,
                    'code': field_line.code,
                    'value': value,
                    'type': type(value),
                }
                lines.append(line_row)
            return lines
        partner_id = self.partner_id
        localdict = {
            **self._get_base_local_dict(),
            **{
                'account': Invoive(partner_id.id, self, self.env),
                'partner': partner_id,
                'company': self.company_id.partner_id,
            }
        }
        provider = self._get_active_tech_provider()
        res = _generate_lines(localdict, provider.line_ids)
        return res

    def _get_tax_by_group(self, group, index=1):
        for line in self.amount_by_group:
            if line[0] and line[0] == group:
                return line[index]
        return 0.0

    def _get_total_type_retention(self):
        res = self._get_dict_by_group(retention=True)
        if not len(res):
            return -1
        result = sum([abs(line['amount']) for line in res])
        return result

    def _get_total_type_transferred(self):
        res = self._get_dict_by_group(retention=False)
        if not len(res):
            return -1
        result = sum([abs(line['amount']) for line in res])
        return result

    def _get_total_type_by_code(self, code):
        res = self._get_dict_by_group()
        result = sum([abs(line['amount']) for line in res
                     if line['code'] == code])
        return result

    def _get_zero_taxes(self):
        self.ensure_one()
        res = {}
        done_taxes = set()
        for line in self.invoice_line_ids:
            price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_ids.compute_all(
                price_unit, quantity=line.quantity, currency=line.currency_id,
                product=line.product_id, partner=line.partner_id
            )
            for tax in taxes['taxes']:
                if tax['amount'] == 0:
                    tax_line_id = self.env['account.tax'].browse(tax['id'])
                    res.setdefault(
                        tax_line_id.id,
                        {
                            'base': 0.0,
                            'amount': 0.0,
                            'rate': tax_line_id.amount,
                            'code': tax_line_id.type_of_tax.code,
                            'name': tax_line_id.type_of_tax.name,
                            'retention': tax_line_id.type_of_tax.retention
                        }
                    )

                    res[tax_line_id.id]['amount'] += tax['amount']
                    res[tax_line_id.id]['base'] += tax['base']
        return res

    def _get_dict_by_group(self, retention=None):
        self.ensure_one()
        lang_env = self.with_context(lang=self.partner_id.lang).env
        tax_lines = self.line_ids.filtered(
            lambda line: line.tax_line_id and
            line.tax_line_id.tax_group_fe != 'nap_fe')
        res = self._get_zero_taxes()
        done_taxes = set()
        for line in tax_lines:
            res.setdefault(
                line.tax_line_id.id,
                {
                    'base': 0.0,
                    'amount': 0.0,
                    'rate': line.tax_line_id.amount,
                    'code': line.tax_line_id.type_of_tax.code,
                    'name': line.tax_line_id.type_of_tax.name,
                    'retention': line.tax_line_id.type_of_tax.retention,
                    'description': line.tax_line_id.description
                }
            )
            res[line.tax_line_id.id]['amount'] += line.price_subtotal
            tax_key_add_base = tuple(
                self._get_tax_key_for_group_add_base(line))
            if tax_key_add_base not in done_taxes:
                if line.currency_id != self.company_id.currency_id:
                    amount = self.company_id.currency_id._convert(
                        line.tax_base_amount, line.currency_id,
                        self.company_id, line.date or fields.Date.today()
                    )
                else:
                    amount = line.tax_base_amount
                res[line.tax_line_id.id]['base'] += amount
                done_taxes.add(tax_key_add_base)
        if retention is None:
            return [res[k] for k in res]
        result = [res[k] for k in res if res[k]['retention'] == retention]
        return result

    def action_test(self):
        pass

    def action_test_api_connect(self):
        provider = self._get_active_tech_provider()
        url = provider.url_download or ''
        request = self._create_api_conection(provider=provider, url=url)
        for record in self:
            if not record.ei_number or not record.type:
                raise ValidationError(
                    _(
                        'This invoice does not have the'
                        '"ei_number" or "type" attribute'
                    )
                )
            response, result, exception = request.download(
                record.type,
                record.ei_number
            )
            api_resp = result.get('response', False)
            if not api_resp or \
               not api_resp.get('representacionGrafica', False) or exception:
                record.message_post(
                    body=_(
                        'An error occurred during the request'
                    )
                )
                continue
            filename = record.ei_number + '.pdf'
            graph_src = api_resp.get('representacionGrafica')
            if not isinstance(graph_src, bytes):
                _file = BytesIO(base64.b64decode(graph_src))
                _file.seek(0)
                graph_src = _file.read()
            record.message_post(
                body=_(
                    'Correct operation of the query to ' +
                    'the asynchronous web service'
                ),
                attachments=[(filename, graph_src)]
            )
            record.write({
                'ei_pdf_base64_bytes': base64.encodestring(graph_src),
                'ei_file_name': filename,
            })

    @api.depends('invoice_date_due', 'date')
    def _compute_is_direct_payment(self):
        for rec in self:
            rec.is_direct_payment = (rec.date == rec.invoice_date_due) \
                and rec.company_id.country_id.code == 'CO'

    def _upload_message_electronic_invoice(self):
        for invoice in self:
            invoice.message_post(
                body=_('Electronic invoice submission.<br/>'),
            )

    def _generate_file(self):
        data = self.generate_dict_invoice_dian()
        provider = self._get_active_tech_provider()

        file = BuilderToFile.prepare_file_for_submission(
            provider.file_extension,
            provider.file_adapter, data,
            provider.file_separator
        )
        return file

    @api.model
    def _create_api_conection(self, provider=None, url=None):
        tech_provider = (
            self._get_active_tech_provider()
                if not provider else provider
        )
        if not url:
            url = provider.url_upload or ''
        result = ApiConnection.prepare_connection(tech_provider,url)
        return result

    def _generate_electronic_invoice_tech_provider(self, attachments=False):
        provider = self._get_active_tech_provider()
        for invoice in self:
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
                invoice.generate_qr_code()

    def _validate_account_move_type(self):
        self.ensure_one()
        return self.type in ('out_invoice', 'out_refund')

    def _validate_sequence_dian(self):
        self.ensure_one()
        sequence = self._get_sequence()
        return (sequence.use_dian_control
                and sequence.dian_type == 'computer_generated_invoice')

    def post(self):
        _now = fields.Datetime.now().replace(second=0)
        for move in self:
            if not move.invoice_date and move.is_sale_document():
                _date = move.ei_invoice_datetime.replace(second=0) \
                    if move.ei_invoice_datetime else _now
                move.invoice_date = _date.strftime('%Y-%m-%d')
                move.ei_invoice_datetime = _date
                move.with_context(check_move_validity=False)\
                    ._onchange_invoice_date()
        res = super(AccountInvoice, self).post()
        if not self.company_id.active_tech_provider:
            return res

        recs_invoice = self.filtered(lambda x: x.is_sale_document())
        for invoice in recs_invoice:
            if invoice.company_id.tax_group_id:
                invoice.validate_required_tax()
            if invoice.type == 'out_refund' and not invoice.ei_origin_id:
                raise UserError(
                    _('You need to add a document reference before posting.')
                )
            today = pytz.utc.localize(_now)
            bogota_tz = pytz.timezone('America/Bogota')
            today = today.astimezone(bogota_tz)
            if (invoice.currency_id.id != invoice.company_currency_id.id and
               invoice.currency_id.date != today.date()):
                raise UserError(
                    _('You need to set the TRM of the day.')
                )
            _lang = invoice.partner_id.lang or 'es_ES'
            ei_amount_text = invoice.ei_amount_text \
                if invoice.ei_amount_text \
                else invoice.currency_id.with_context(lang=_lang)\
                .amount_to_text(invoice.amount_total)

            sequence = invoice._get_sequence()
            sequence_date = invoice.date or invoice.invoice_date
            prefix, dummy = sequence._get_prefix_suffix(
                date=sequence_date, date_range=sequence_date)
            number_next = invoice.name.replace(prefix, "")

            to_write = {
                'ei_serie': prefix,
                'ei_folio': number_next,
                'ei_amount_text': ei_amount_text
            }
            invoice.write(to_write)
            for line in invoice.advances_line_ids:
                invoice.js_assign_outstanding_line(line.id)

        provider = self._get_active_tech_provider()
        if not provider:
            raise UserError(
                _('Please configure technology provider '
                  'for electronic invoicing')
            )
        to_process = self.filtered(
            lambda move: move._validate_account_move_type()
            and move._validate_sequence_dian())
        if to_process:
            to_process._generate_electronic_invoice_tech_provider(
                self.attachments
            )

        return res

    def get_category_to_apply(self):
        buyer_tx_liability = self.partner_id.fiscal_responsibility
        seller_tx_liability = self.company_id.partner_id.fiscal_responsibility
        lines = seller_tx_liability.line_ids.filtered(
            lambda line: line.fiscal_responsability_id == buyer_tx_liability)
        return lines.applicable_tax

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        super(AccountInvoice, self)._onchange_partner_id()
        for line in self.invoice_line_ids:
            line.tax_ids = line._get_computed_taxes()

    def _get_surchange_discount_data(self):
        return super(AccountInvoice, self)._get_surchange_discount_data()

    def action_cron_get_document_invoices(self):
        date_act = fields.Datetime.now()
        last_notif_mail = fields.Datetime.to_string(
            self.env.context.get('lastcall') or date_act)
        invoices = self.env['account.move'].search([
            ('ei_number', '!=', False),
            ('invoice_status', '=', 'accepted'),
            ('ei_pdf_base64_bytes', '=', False),
            ('type', 'in', ['out_invoice', 'out_refund'])
        ])
        if len(invoices) == 0:
            return
        provider = self._get_active_tech_provider()
        tech_provider_request = ApiConnection.prepare_connection(provider)
        for invoice in invoices:
            response, result, exception = tech_provider_request.download(
                invoice._get_ei_type_dian(),
                invoice.ei_number
            )
            api_resp = result.get('response', False)
            if not api_resp or \
               not api_resp.get('representacionGrafica', False) or exception:
                invoice.message_post(
                    body=_(
                        'An error occurred during the request'
                    )
                )
                continue
            filename = invoice.ei_number + '.pdf'
            filename2 = invoice.ei_number + '.xml'
            graph_src = api_resp.get('representacionGrafica')
            if graph_src is not None and not isinstance(graph_src, bytes):
                _file = BytesIO(base64.b64decode(graph_src))
                _file.seek(0)
                graph_src = _file.read()
            invoice.message_post(
                body=_(
                    'Correct operation of the query to ' +
                    'the asynchronous web service'
                ),
                attachments=[(filename, graph_src)]
            )
            app_resp_doc = api_resp.get(
                'representacionGraficaAppResponse', False)
            if app_resp_doc is not None and \
               not isinstance(app_resp_doc, bytes):
                _file = BytesIO(base64.b64decode(app_resp_doc))
                _file.seek(0)
                app_resp_doc = _file.read()

            app_resp = api_resp.get('appResponse', False)
            if app_resp is not None and not isinstance(app_resp, bytes):
                _file = BytesIO(base64.b64decode(app_resp))
                _file.seek(0)
                app_resp = _file.read()

            dian_ubl = api_resp.get('ubl', False)
            if dian_ubl is not None and not isinstance(dian_ubl, bytes):
                _file = BytesIO(base64.b64decode(dian_ubl))
                _file.seek(0)
                dian_ubl = _file.read()

            base64_1 = base64.encodestring(app_resp) if\
                isinstance(app_resp, bytes) else False
            base64_2 = base64.encodestring(dian_ubl) if\
                isinstance(dian_ubl, bytes) else False
            base64_3 = base64.encodestring(app_resp_doc) if\
                isinstance(app_resp_doc, bytes) else False
            base64_4 = base64.encodestring(graph_src) if\
                isinstance(graph_src, bytes) else False

            invoice.write({
                'ei_app_resp_file_name': 'app_resp_' + filename2,
                'ei_application_response_base64_bytes': base64_1,
                'ei_dian_resp_file_name': 'ubl_' + filename2,
                'ei_dian_response_base64_bytes': base64_2,
                'ei_dian_document_file_name': 'comprobante_dian_' + filename,
                'ei_attached_document_base64_bytes': base64_3,
                'ei_file_name': filename,
                'ei_pdf_base64_bytes': base64_4,
                'ei_status_code': api_resp.get('codigo', ''),
                'ei_status_description': api_resp.get('descripcion', ''),
                'ei_status_message': api_resp.get('estatusDocumento', ''),
            })

    def action_post_with_files(self):
        self.ensure_one()
        if (
            self.type in ['out_invoice', 'out_refund'] and
            self._get_active_tech_provider()
        ):
            compose_form = self.env.ref(
                'l10n_co_account_e_invoice.support_files_send_wizard_form',
                raise_if_not_found=False
            )
            provider = self._get_active_tech_provider()
            ctx = dict(
                message=_(
                    'For the technology provider %s '
                    'the number of support files is: %s'
                    % (provider.name, provider.num_doc_attachs)
                ),
                invoice_id=self.id,
            )
            return {
                'name': _('Send Support Filess'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'support.files.send',
                'views': [(compose_form.id, 'form')],
                'view_id': compose_form.id,
                'target': 'new',
                'context': ctx,
            }
        else:
            raise ValidationError(
                _(
                    'There is no technology provider configured'
                )
            )

    def _action_post_files(self, attachments, reconcile_line_ids,
                           note='', extra_refs=False):
        self.ensure_one()
        self.attachments = attachments
        self.ei_ubl_note = note
        self.advances_line_ids = reconcile_line_ids
        self.extra_ref_ids = extra_refs \
            if extra_refs and len(extra_refs) > 0 else False
        super(AccountInvoice, self).action_post()
        if attachments:
            attachments_message = list()
            for attach in attachments:
                attachments_message.append(
                    (attach.name, base64.b64decode(attach.datas))
                )
            self.message_post(
                body=_('These are the support files that are attached<br/>'),
                attachments=attachments_message
            )

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

    @api.onchange('ei_qr_data')
    def generate_qr_code(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=2,
            border=2,
        )
        qr.add_data(self.ei_qr_data)
        qr.make(fit=True)
        img = qr.make_image()
        temp = BytesIO()
        img.save(temp, format="PNG")
        qr_image = base64.b64encode(temp.getvalue())
        self.ei_qr_image = qr_image
        self._get_text_info()

    def _get_ei_type_dian(self):
        _ref = 'l10n_co_account_e_invoice.l10n_co_type_documents_'
        if (
            self.type == 'out_invoice' and
            self.ei_type_document_id.id != self.env.ref(_ref + '6').id
        ):
            return self.type
        return 'out_refund_credit'\
            if self.ei_type_document_id.id == self.env.ref(_ref + '5').id\
            else 'out_refund_debit'

    @api.depends('ei_invoice_datetime')
    def compute_query_deadline(self):
        for record in self:
            provider = record._get_active_tech_provider()
            date = (
                record.ei_invoice_datetime +
                timedelta(days=provider.num_of_days_to_validate)
            )
            record.status_inquiry_deadline = date

    def action_cron_get_acceptance_status(self):
        date_act = fields.Datetime.now()
        last_notif_mail = fields.Datetime.to_string(
            self.env.context.get('lastcall') or date_act)
        invoices = self.env['account.move'].search([
            ('status_inquiry_deadline', '>=', date_act),
            ('invoice_status', '=', 'accepted'),
            ('type', 'in', ['out_invoice', 'out_refund'])
        ])
        if len(invoices) == 0:
            return
        provider = self._get_active_tech_provider()
        tech_provider_request = ApiConnection.prepare_connection(provider)
        for invoice in invoices:
            invoice_status = tech_provider_request.validate_status(
                invoice.type,
                invoice.ei_number
            )
            if not invoice_status:
                continue
            if invoice_status != invoice.ei_status_message:
                invoice.message_post(
                    body=_(
                        'The acceptance status of the invoice'
                        'changed from %s to %s' % (
                            invoice.ei_status_message
                            if invoice.ei_status_message else "''",
                            invoice_status
                        )
                    )
                )
            invoice.write({
                'ei_status_message': invoice_status,
            })

    def validate_final_acceptance_status(self):
        date_act = fields.Datetime.now()
        last_notif_mail = fields.Datetime.to_string(
            self.env.context.get('lastcall') or date_act)
        invoices = self.env['account.move'].search([
            ('status_inquiry_deadline', '<', date_act),
            ('invoice_status', '=', 'accepted'),
            ('type', 'in', ['out_invoice', 'out_refund']),
            ('ei_status_message', '!=', 'Aceptada')
        ])
        if len(invoices) == 0:
            return
        for invoice in invoices:
            if (
                invoice.ei_status_message == 'Enviado a Adquiriente' or
                invoice.ei_status_message == 'Fiscalmente Valido' or
                invoice.ei_status_message == ''
            ):
                invoice.ei_status_message = 'Aceptada'
                invoice.message_post(
                    body=_(
                        'The acceptance deadline is over, which is why the'
                        ' invoice status is "Accepted"'
                    )
                )

    def l10n_co_log_rejected_invoice_connection(self, descripcion):
        if not self._context.get('not_auto_commit', False):
            self.env.cr.rollback()
        with self.pool.cursor() as cr:
            self.with_env(self.env(cr=cr, user=SUPERUSER_ID)).message_post(
                body=_('Connection error:<br/>%s') % descripcion)
            self.with_env(self.env(cr=cr, user=SUPERUSER_ID)).write({
                'invoice_status': 'rejected'})
        raise UserError(_(
            'The connection is down '
            'more information, please contact the '
            'administrator.\nError: %s' % descripcion
        ))

    def validate_required_tax(self):
        self.ensure_one()
        group = self.company_id.tax_group_id
        for line in self.invoice_line_ids:
            iva = line._get_data_taxes_e_invoice_line(group.name)
            if len(iva) == 0:
                raise UserError(
                    _('You need to add a Iva taxes before posting.')
                )

    @api.onchange(
        'partner_id',
        'currency_id',
        'company_currency_id')
    def _compute_ei_amount_text(self):
        self.ensure_one()
        _lang = self.partner_id.lang or 'es_ES'
        self.ei_amount_text = self.currency_id.with_context(
            lang=_lang).amount_to_text(self.amount_total) \
            if self.currency_id else ''

    @api.depends(
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state')
    def _compute_amount(self):
        super(AccountInvoice, self)._compute_amount()
        for invoice in self:
            invoice._compute_ei_amount_text()

        # recs_invoice = self.filtered(lambda x: x.is_sale_document())
        # for invoice in recs_invoice:
        #     for line in invoice.invoice_line_ids:
        #         line.name = invoice.ref

    def _get_advance_values(self):
        self.ensure_one()
        reconciled_vals = self._get_reconciled_info_JSON_values()
        for line in reconciled_vals:
            payment_id = self.env['account.payment'].browse(
                line['account_payment_id'])
            line.update({
                'currency_code': payment_id.currency_id.name
            })
        return reconciled_vals

    def _get_total_advance(self):
        self.ensure_one()
        res = self._get_reconciled_info_JSON_values()
        result = sum([abs(line['amount']) for line in res])
        return result

    @api.depends('operation_type', 'ei_type_document_id')
    @api.onchange('operation_type', 'ei_type_document_id')
    def compute_debit_credit_note_visible(self):
        for record in self:
            record.is_debit_note = False
            record.is_credit_note = False
            if (
                record.ei_type_document_id in
                record.company_id.account_type_documents_for_credit_note
            ):
                record.is_credit_note = True
                record.is_debit_note = False
            elif (
                record.ei_type_document_id in
                record.company_id.account_type_documents_for_debit_note
            ):
                record.is_debit_note = True
                record.is_credit_note = False
            record.is_visible_deb_cred_note = True\
                if record.is_debit_note != record.is_credit_note else False
