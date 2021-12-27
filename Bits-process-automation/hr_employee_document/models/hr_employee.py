from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    documents_employee_ids = fields.One2many(
        'hr.employee.document.line', 'employee_id', string="Documents")
