# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _
import json


class POS(models.Model):
    _inherit = "sale.order"

    @api.model
    def invoice_origin_pos_to_post(self, invoice_id):
        posted = False
        invoice = self.env['account.move'].search(
            [
                ('id', '=', str(invoice_id.get('invoice_id')))
            ]
        )
        if invoice:
            invoice.action_post()
            posted = True
        return json.dumps({
            'posted': posted
        })
