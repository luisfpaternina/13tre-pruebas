# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    town_from_ids = fields.Many2many(
        'res.country.town', 'delivery_carrier_town_from_rel',
        'carrier_id', 'town_from_id', 'Towns from',
        domain="[('state_id', 'in', state_ids)]")

    def _match_address(self, partner):
        self.ensure_one()
        result = super(DeliveryCarrier, self)._match_address(partner)
        context = partner._context
        sale_order = self.env['sale.order'].search(
            [('id', '=', context.get('default_order_id', False))])
        if (self.town_from_ids and context.get(
                'default_order_id', False) and sale_order.town_id
                not in self.town_from_ids):
            return False

        return result
