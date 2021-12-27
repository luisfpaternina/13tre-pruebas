# -*- coding: utf-8 -*-

from odoo import fields, api, models


class IrSequenceDateRange(models.Model):
    _inherit = 'ir.sequence.date_range'

    prefix = fields.Char(string='Prefix')
    resolution_number = fields.Char(string='Resolution Number')
    number_from = fields.Integer(string='Initial Number')
    number_to = fields.Integer(string='Final Number')
    active_resolution = fields.Boolean(string='Active Resolution?')

    @api.onchange('number_from')
    def _onchange_number_from(self):
        self.ensure_one()
        if self.number_from > 0:
            self.number_next_actual = self.number_from
