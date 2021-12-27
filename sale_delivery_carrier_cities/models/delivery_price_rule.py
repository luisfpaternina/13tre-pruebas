# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class DeliveryPriceRule(models.Model):
    _inherit = 'delivery.price.rule'

    variable = fields.Selection(
        selection_add=[('price_kilogram', 'Price kilogram * Weight')])
    variable_factor = fields.Selection(
        selection_add=[('price_kilogram', 'Price kilogram * Weight')])
