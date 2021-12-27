# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _is_excess_budget(self):
        for line in self:
            line.is_excess_budget = line._verificate_order_line_budget()

    is_excess_budget = fields.Boolean(compute='_is_excess_budget')

    crossovered_budget_line_id = fields.Many2one(
        'crossovered.budget.lines',
        'Budget line',
    )

    def _verificate_order_line_budget(self):
        localdict = dict()

        date_order = self.order_id.date_order.date()
        budget_lines = self.env['crossovered.budget.lines'].search([
            ('analytic_account_id', '=', self.account_analytic_id.id),
            ('date_from', '<=', date_order),
            ('date_to', '>=', date_order),
        ])
        account_expense_id = self.product_id.property_account_expense_id.id
        lines = budget_lines.filtered(
            lambda line: account_expense_id in
            line.general_budget_id.account_ids.ids
        )
        if not lines or len(lines) == 0:
            return True

        for line in lines:
            res = abs(line.planned_amount) - abs(line.practical_amount)
            if res >= abs(self.price_subtotal):
                self.crossovered_budget_line_id = line.id
                return False

        return True
