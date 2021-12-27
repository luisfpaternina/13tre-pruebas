from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class HrPayrollRetentionLine(models.Model):
    _name = 'hr.payroll.retention.line'

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    uvt_maximum = fields.Integer(string='UVT Maximum')
    maximum_percentage = fields.Integer(string="Maximum Percentage")
    salary_rule_ids = fields.Many2many(
        string='Salary Rules',
        comodel_name='hr.salary.rule',
    )
    retention_id = fields.Many2one('hr.payroll.retention', string="Retencion")
    document_code = fields.Char(string='Document Code')
