from odoo import models, fields, api


class HrPayrollNews(models.Model):
    _inherit = 'hr.payroll.news'

    holiday_history_id = fields.Many2one(
        'hr.payroll.holidays.history',
        string='Holiday history')
