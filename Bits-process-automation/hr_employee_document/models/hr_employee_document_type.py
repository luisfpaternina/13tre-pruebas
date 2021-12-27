from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrEmployeeDocumentType(models.Model):
    _name = 'hr.employee.document.type'

    def _get_default_company(self):
        return self.env.company.id

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    company_id = fields.Many2one(
        'res.company', 'Company', index=True,
        default=_get_default_company)
