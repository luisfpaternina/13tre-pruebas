# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class account_payment(models.Model):
    _inherit = "account.payment"

    def post(self):

        active_ids = self.env.context.get('active_ids')
        active_model = self.env.context.get('active_model')

        if active_model and active_model == 'account.move' and active_ids:
            move_ids = self.env['account.move'].browse(active_ids)
            for move in move_ids:
                line_id = self.env['credit.line'].search([
                    ('receipt_id', '=', move.id)
                ])
                if line_id:
                    paid = True
                    for line in line_id.credit_id.credit_lines:
                        if line != line_id and line.receipt_id.amount_residual:
                            paid = False
                    if paid:
                        line_id.credit_id.state = 'paid_out'

                    if line_id.credit_id.modality == 'revolving':
                        actual_balance = line_id.credit_id.available_balance
                        refund_balance = line_id.capital_subscription
                        new_refund_balance = actual_balance + refund_balance
                        if new_refund_balance > line_id.credit_id.credit_limit:
                            line_id.credit_id.available_balance = (
                                line_id.credit_id.credit_limit
                            )
                        else:
                            line_id.credit_id.available_balance = (
                                actual_balance + refund_balance
                            )
        
        return super(account_payment, self).post()
