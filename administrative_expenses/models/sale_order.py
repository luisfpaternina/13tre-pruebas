from odoo import models, fields, api, _
import logging

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
