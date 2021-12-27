# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    invoice_name = fields.Char(
        string="Invoice name",
        related="sale_id.invoice_ids.display_name")
    invoice_state = fields.Selection(
        string="Invoice state",
        related="sale_id.invoice_ids.invoice_payment_state")
    is_validate = fields.Boolean(
        string="Validate")
