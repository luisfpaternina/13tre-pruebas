# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _prepare_invoice_values(self, order, name, amount, so_line):
        result = super(SaleAdvancePaymentInv, self)._prepare_invoice_values(
            order, name, amount, so_line)
        result['town_id'] = order.town_id.id

        return result
