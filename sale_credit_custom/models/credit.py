# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class Credit(models.Model):
    _inherit = 'credit'

    expenses_acum = fields.Float()
    invoice_ids = fields.One2many(
        'account.move',
        'credit'
    )

    @api.onchange('credit_limit', 'invoice_ids')
    def calculate_expenses_acum(self):
        self.ensure_one()
        acum = 0
        for invoice in self.invoice_ids:
            if invoice.state == 'posted':
                acum += invoice.amount_total
        self.expenses_acum = acum
        self._calculate_avalaible_balance()

    def _calculate_avalaible_balance(self):
        self.available_balance = self.credit_limit - self.expenses_acum
