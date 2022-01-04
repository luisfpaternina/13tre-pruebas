# -*- coding: utf-8 -*-

import json

import werkzeug.urls
import werkzeug.utils
from odoo.http import request
from odoo.tools import image_process

import odoo
from odoo import fields, models, http
from odoo.addons.auth_oauth.controllers.main import OAuthLogin


class SaleOrder(models.Model):
    _inherit = "sale.order"

    metodo_pago_web_transaccion = fields.Char(string="Método de pago", default="")

    # products_ids = fields.Many2many('product.template', help="Unión de productos", string="Productos")

    # def _get_method_payment_in_transaction(self):
    #     for record in self:
    #         order_id = record.id
    #         if order_id:
    #             transaccion = self.env['payment.transaction'].search([('sale_order_ids', 'in', order_id)])
    #             if transaccion:
    #                 if transaccion.acquirer_id:
    #                     return transaccion.acquirer_id.display_name