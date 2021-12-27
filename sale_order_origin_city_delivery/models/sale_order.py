# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    town_id = fields.Many2one('res.country.town', string=_('Town from'))

    def _prepare_invoice(self):
        result = super(SaleOrder, self)._prepare_invoice()
        result['town_id'] = self.town_id

        return result

    @api.onchange('company_id')
    def _get_town_id(self):
        domain = [('country_id', '=', self.company_id.country_id.id)]

        return {'domain': {'town_id': domain}}
