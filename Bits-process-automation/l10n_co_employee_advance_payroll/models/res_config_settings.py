# -*- coding: utf-8 -*-

from datetime import date
from ast import literal_eval

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    integral_structure_type_payroll_ids = fields.Many2many(
        'hr.payroll.structure.type',
        'hr_payroll_integral_structure_type_ids_table',
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        with_user = self.env['ir.config_parameter'].sudo()
        rules = [
            'integral_structure_type_payroll_ids',
        ]
        for rule in rules:
            rule_id = with_user.get_param('many2many.' + rule)
            res[rule] = [(6, 0, literal_eval(rule_id))] \
                if rule_id else False
        return res

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.integral_structure_type_payroll_ids',
            self.integral_structure_type_payroll_ids.ids)
        return res
