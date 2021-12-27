# -*- coding: utf-8 -*-
from ast import literal_eval
from odoo import models, fields, api, _


class HrPayrollNewsSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_bits_hr_payroll_news_related = fields.Boolean(
        string="Integrate Payroll News"
    )

    integrate_payroll_news = fields.Boolean(
        string='Integrate to Payroll',
        default=False,
        config_parameter="hr_payroll.integrate_payroll_news"
    )

    module_bits_hr_contract_advance = fields.Boolean(
        string="Integrate contract advance",
        default=False
    )

    rounding_rule_ids = fields.Many2many(
        'hr.salary.rule',
        'rounding_rule_ids_table'
    )

    basic_salary = fields.Float(
        string='basic salary', related="company_id.basic_salary",
        readonly=False)

    @api.model
    def get_values(self):
        res = super(HrPayrollNewsSettings, self).get_values()
        with_user = self.env['ir.config_parameter'].sudo()
        rules = [
            'rounding_rule_ids'
        ]
        for rule in rules:
            rule_id = with_user.get_param('many2many.' + rule)
            res[rule] = [(6, 0, literal_eval(rule_id))] \
                if rule_id else False
        return res

    def set_values(self):
        res = super(HrPayrollNewsSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.rounding_rule_ids', self.rounding_rule_ids.ids)
        return res
