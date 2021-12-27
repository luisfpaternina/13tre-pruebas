# -*- coding: utf-8 -*-

from datetime import date
from ast import literal_eval

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    rule_contrib_pension = fields.Many2many(
        'hr.salary.rule',
        'rule_contrib_pension_table',
        string='Contrib pensions rules',
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        with_user = self.env['ir.config_parameter'].sudo()
        rule_contrib_pension = with_user.get_param(
            'many2many.rule_contrib_pension')
        res.update(
            rule_contrib_pension=[(6, 0, literal_eval(rule_contrib_pension))]
            if rule_contrib_pension else False
        )
        return res

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.rule_contrib_pension',
            self.rule_contrib_pension.ids)
        return res
