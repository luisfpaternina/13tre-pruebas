# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    invoice_name = fields.Char(
        string="Invoice",
        related="sale_id.invoice_ids.display_name")