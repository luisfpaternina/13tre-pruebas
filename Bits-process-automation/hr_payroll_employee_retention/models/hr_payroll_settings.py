# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta


class HrPayrollSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    parameter_retention_id = fields.Many2one(
        string='Parameter Retention',
        comodel_name='hr.payroll.parameter.retention',
        config_parameter="hr_payroll.parameter_retention_id"
    )
    withholding_wage_rule_id = fields.Many2one(
        string='Withholding Wage Rule',
        comodel_name='hr.salary.rule',
        config_parameter="hr_payroll.withholding_wage_rule_id"
    )

    str_date_truncate = fields.Char()
    str_date_exec = fields.Char()
    str_date_prev = fields.Char(
        comodel_name='hr.payroll.employee.retention',
        config_parameter="hr_payroll_employee_retention.str_date_prev",
        readonly=True
    )

    date_truncate = fields.Date(
        default=datetime.now().strftime('%Y-%m-01')
    )
    date_execute = fields.Date(
        default=str(datetime.now() + relativedelta(
            months=+1, day=1, days=-1))[:10]
    )

    def set_values(self):
        super(HrPayrollSettings, self).set_values()
        set_param = self.env['ir.config_parameter'].set_param

        if self.date_truncate:
            str_date_truncate = self.date_truncate.strftime('%Y-%m-%d')
            set_param('str_date_truncate', str_date_truncate)

        if self.date_execute:
            str_date_exec = self.date_execute.strftime('%Y-%m-%d')
            set_param('str_date_exec', str_date_exec)

    @api.model
    def get_values(self):
        res = super(HrPayrollSettings, self).get_values()
        get_param = self.env['ir.config_parameter'].sudo().get_param

        str_date = get_param('str_date_truncate', default='')
        str_date_exec = get_param('str_date_exec', default='')

        date_truncate = False \
            if str_date == '' \
            else datetime.strptime(str_date, '%Y-%m-%d').date()
        date_execute = False \
            if str_date_exec == '' \
            else datetime.strptime(str_date_exec, '%Y-%m-%d').date()
        res.update(
            date_truncate=date_truncate,
            date_execute=date_execute,
        )
        return res
