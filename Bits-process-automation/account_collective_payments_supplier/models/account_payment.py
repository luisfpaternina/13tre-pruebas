from odoo import models, fields, api, _


class AccountPayment(models.Model):
    _inherit = "account.payment"

    account_collective_payments_supplier_id = fields.Many2one(
        'account.collective.payments.supplier',
        string=_('Payment to Supplier')
    )
