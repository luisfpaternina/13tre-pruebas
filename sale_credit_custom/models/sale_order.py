# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrderCustom(models.Model):
    _inherit = 'sale.order'

    warning = fields.Boolean(
        default=False
    )

    @api.onchange('partner_id')
    def calculate_credit_allow(self):
        self.ensure_one()
        self.warning = False
        credits_available = self.partner_id.credit_ids
        credit_active = 0
        for credit in credits_available:
            credit_active += (
                1 if credit.state == 'active' else 0
            )
        if credit_active >= 1:
            self.warning = True
