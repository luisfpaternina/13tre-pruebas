# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    town_id = fields.Many2one('res.country.town', string=_('Town from'))

    @api.onchange('company_id')
    def _get_town_id(self):
        domain = [('country_id', '=', self.company_id.country_id.id)]

        return {'domain': {'town_id': domain}}
