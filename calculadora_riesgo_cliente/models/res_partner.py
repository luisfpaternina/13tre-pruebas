# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class ResPartner(models.Model):
    _inherit = ['res.partner']

    riesgo_concedido = fields.Float(
        string='Riesgo Concedido',
        required=False, default=0)
    riesgo_disponible = fields.Float(
        string='Riesgo Disponible',
        required=False, compute="_get_available_risk", default=0)

    def _get_available_risk(self):

        partner_id = self['id']
        total_a_restar = 0
        SO = self.env['sale.order']
        # AM = self.env['account.move']

        total_consumido_pedidos_venta = 0
        # total_disponible_facturas = self.get_total_pagado_facturas()
        total_pendiente_facturas = self.total_due

        orders = SO.search([('partner_id', '=', partner_id)])

        if orders:
            for order in orders:
                state = order.state
                if (state == "sale" or state == "done") and order.invoice_status != "invoiced":
                    if order.invoice_status != "no":
                        total_consumido_pedidos_venta = total_consumido_pedidos_venta + order.amount_total
        total_a_restar = total_pendiente_facturas + total_consumido_pedidos_venta

        self['riesgo_disponible'] = self.riesgo_concedido - total_a_restar

    def get_total_pagado_facturas(self):

        cliente = self.id

        invoice_total_for_sum = 0
        AM = self.env['account.move']
        AML = self.env['account.move.line']

        facturas = AM.search([('partner_id', '=', cliente)])

        if facturas:
            for factura in facturas:
                factura_id = factura.id
                lineas = AML.search([('move_id.id', '=', factura_id)])
                if lineas:
                    for linea in lineas:
                        if linea.account_internal_type == "receivable":
                            if linea.amount_residual != abs(linea.price_total):
                                invoice_total_for_sum = invoice_total_for_sum + (
                                        abs(linea.price_total) - linea.amount_residual)

        return invoice_total_for_sum