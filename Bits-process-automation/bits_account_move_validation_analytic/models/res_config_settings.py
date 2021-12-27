# -*- coding: utf-8 -*-

from datetime import date
from ast import literal_eval

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    user_type_ids = fields.Many2many(
        'account.account.type',
        'user_type_ids_table',
        string='Type',
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        with_user = self.env['ir.config_parameter'].sudo()
        user_type_ids = with_user.get_param('many2many.user_type_ids')
        res.update(
            user_type_ids=[(6, 0, literal_eval(user_type_ids))]
            if user_type_ids else False
        )
        return res

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.user_type_ids', self.user_type_ids.ids)
        return res
