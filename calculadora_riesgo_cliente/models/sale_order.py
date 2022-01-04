# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date


class SaleOrder(models.Model):
    _inherit = ['sale.order']

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        # Para activar el modal, el cliente debe de tener el credito disponible a 0
        cliente = self.partner_id
        total_pedido = self.amount_total

        if cliente.riesgo_disponible <= 0 or total_pedido > cliente.riesgo_disponible:
            raise ValidationError(_("Lo sentimos, no puede confirmar el pedido. Este cliente ha superado el limite de riesgo concedido"))
        else:
            return res

        #return res