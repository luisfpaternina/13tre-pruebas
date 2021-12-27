# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields


class AccountInvoiceReport(models.Model):

    _inherit = 'account.invoice.report'

    pay_total = fields.Float(string='Pay Total', readonly=True)

    def _select(self):
        return super()._select() + ", (move.amount_total_signed - \
        move.amount_residual_signed) as pay_total"
