# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    town_to_ids = fields.Many2many(
        'res.country.town', 'delivery_carrier_town_to_rel',
        'carrier_id', 'town_to_id', 'Towns to',
        domain="[('state_id', 'in', state_ids)]")
    price_kilogram = fields.Float("Price kilogram", default=0)

    def _match_address(self, partner):
        self.ensure_one()
        result = super(DeliveryCarrier, self)._match_address(partner)
        if self.town_to_ids and partner.town_id not in self.town_to_ids:
            return False

        return result

    @api.onchange('delivery_type')
    def _onchange_delivery_type(self):
        if self.delivery_type == 'fixed':
            self.price_kilogram = 0

    def _get_price_from_picking(self, total, weight, volume, quantity):
        price = 0
        criteria_found = False
        price_dict = {
            'price': total, 'volume': volume,
            'weight': weight, 'wv': volume * weight, 'quantity': quantity,
            'price_kilogram': self.price_kilogram * weight}
        for line in self.price_rule_ids:
            test = safe_eval(line.variable + line.operator +
                             str(line.max_value), price_dict)
            if test:
                price = line.list_base_price + line.list_price * \
                    price_dict[line.variable_factor]
                criteria_found = True
                break
        if not criteria_found:
            raise UserError(
                _("No price rule matching this order; delivery cost "
                  "cannot be computed."))

        return price
