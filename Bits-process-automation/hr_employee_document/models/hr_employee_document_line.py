from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrEmployeeDocumentLine(models.Model):
    _name = 'hr.employee.document.line'

    def _get_default_company(self):
        return self.env.company.id

    @api.model
    def _get_dafault_currency(self):
        return self.env.company.currency_id.id

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency', default=_get_dafault_currency)
    name = fields.Char(string='Name', required=True,
                       related='document_type_id.name')
    description = fields.Char(string='Description')
    employee_id = fields.Many2one(string='Employee',
                                  comodel_name='hr.employee')
    document_type_id = fields.Many2one(
        string="Document", comodel_name='hr.employee.document.type',
        required=True)
    expiration_date = fields.Date(string='Expiration Date')
    state = fields.Selection(string='State', selection=[(
        'enabled', 'Enabled'), ('disabled', 'Disabled')], required=True,
        default='enabled')
    company_id = fields.Many2one(
        'res.company', 'Company', index=True,
        default=_get_default_company)
    amount_contributibe = fields.Monetary(
        string="Amount Contributibe", currency_field='currency_id')
