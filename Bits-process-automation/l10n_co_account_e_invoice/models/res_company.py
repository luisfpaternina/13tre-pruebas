# coding: utf-8
from odoo import fields, models

TEMPLATE_CODE = [
    ('01', 'CGEN03'),
    ('02', 'CGEN04'),
]


class ResCompany(models.Model):
    _inherit = 'res.company'

    template_code = fields.Selection(
        TEMPLATE_CODE,
        string="Colombia Template Code"
    )

    def _get_template_code_description(self):
        return dict(TEMPLATE_CODE).get(self.template_code)

    trade_name = fields.Char(
        string="Business name",
        default="")
    digital_certificate = fields.Text(
        string="Public digital certificate",
        default="")
    operation_type = fields.Selection([
        ('01', 'Fuel'),
        ('02', 'Issuer is Self-retaining'),
        ('03', 'Excluded and Exempt'),
        ('04', 'Export'),
        ('05', 'Generic'),
        ('06', 'Generic with advance payment'),
        ('07', 'Generic with billing period'),
        ('08', 'Consortium'),
        ('09', 'Services AIU'),
        ('10', 'Standard'),
        ('11', 'Mandates goods'),
        ('12', 'Mandates Services')],
        string='DIAN operation type')

    active_tech_provider = fields.Boolean()

    account_sale_tax_ids = fields.Many2many(
        'account.tax',
        string="Default Sale Tax"
    )

    header_regimen_activity = fields.Char(
        string="Regimen Activity",
        translate=True
    )
    header_rate = fields.Char(
        string="Rate",
        translate=True
    )
    header_decree = fields.Char(
        stirng="Decree",
        translate=True
    )

    tax_group_id = fields.Many2one(
        'account.tax.group',
        string="Tax Group"
    )

    account_type_documents_for_invoice = fields.Many2many(
        'l10n_co.type_documents',
        'res_company_type_documents_invoice_rel',
        'res_company_id',
        'type_documents_id',
        string="Types of Documents for Invoice"
    )

    account_type_documents_for_credit_note = fields.Many2many(
        'l10n_co.type_documents',
        'res_company_type_documents_credit_note_rel',
        'res_company_id',
        'type_documents_id',
        string="Types of Documents for Credit Note"
    )

    account_type_documents_for_debit_note = fields.Many2many(
        'l10n_co.type_documents',
        'res_company_type_documents_debit_note_rel',
        'res_company_id',
        'type_documents_id',
        string="Types of Documents for Debit Note"
    )
