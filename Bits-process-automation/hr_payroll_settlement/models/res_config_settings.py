# -*- coding: utf-8 -*-

from datetime import date
from ast import literal_eval

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    rule_unpaid_ids = fields.Many2many(
        'hr.salary.rule',
        'rule_unpaid_ids_table',
        string='Unpaid rules',
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        with_user = self.env['ir.config_parameter'].sudo()
        rule_unpaid_ids = with_user.get_param('many2many.rule_unpaid_ids')
        res.update(
            rule_unpaid_ids=[(6, 0, literal_eval(rule_unpaid_ids))]
            if rule_unpaid_ids else False
        )
        return res

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.rule_unpaid_ids', self.rule_unpaid_ids.ids)
        return res
