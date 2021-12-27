# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    estado_factura = fields.Char(related="sale_id.invoice_ids[0].invoice_payment_state", string="Estado Factura")    
    factura = fields.Char(related="sale_id.invoice_ids[0].display_name", string="Factura")