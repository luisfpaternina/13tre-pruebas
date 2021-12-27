# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from ast import literal_eval


class HrPayslip(models.Model):

    _inherit = 'hr.payslip'

    pensions_contrib = fields.Boolean(
        default=False,
        string="Not Obliged Contribute Pensions",
        related="employee_id.pensions_contrib")

    def _get_calculate_payslip_lines(self, values):
        if self.pensions_contrib:
            rules = list(values)
            exclude_rule = self.env['ir.config_parameter'].sudo()\
                .get_param('many2many.rule_contrib_pension')
            rule_contrib_pension = literal_eval(exclude_rule) if \
                exclude_rule else []
            values = filter(
                lambda x: x['salary_rule_id'] not in rule_contrib_pension,
                rules)
        return super(HrPayslip, self)._get_calculate_payslip_lines(values)
