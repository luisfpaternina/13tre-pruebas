from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class HrPayrollRetention(models.Model):
    _name = 'hr.payroll.retention'

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)
    description = fields.Char(string="Description")
    line_ids = fields.One2many(
        'hr.payroll.retention.line', 'retention_id', string="Retention Items")
