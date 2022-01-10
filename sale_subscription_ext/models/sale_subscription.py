# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    city = fields.Char(string="City",related="partner_id.city")
