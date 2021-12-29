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
        string="Validate",
        compute="_validate_invoice_state")


    @api.depends('invoice_state','name')
    def _validate_invoice_state(self):
        for record in self:
            if record.picking_type_id.sequence_code == 'OUT':
                if record.invoice_state == 'paid':
                    record.is_validate = True
                else:
                    record.is_validate = False
            else:
                record.is_validate = False
