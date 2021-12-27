# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountCollectivePaymentsSupplier(models.Model):
    _name = 'account.collective.payments.supplier'

    name = fields.Char(
        string=_("Name"),
        readonly=True
    )
    payment_type = fields.Char(
        string=_("Payment Type"),
        readonly=True
    )
    payment_date = fields.Date(
        string=_("Payment Date"),
        readonly=True
    )
    payment_way_dian_id = fields.Many2one(
        "payment.way",
        string=_("Payment Way"),
        readonly=True
    )
    payment_method_dian_id = fields.Many2one(
        "payment.method",
        string=_("Payment Method"),
        readonly=True
    )
    journal_id = fields.Many2one(
        "account.journal",
        string=_("Journal"),
        readonly=True
    )
    company_id = fields.Many2one(
        "res.company",
        string=_("Company"),
        readonly=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        readonly=True,
        compute="_compute_currency",
        store=True)
    amount = fields.Monetary(
        string=_("Amount"),
        compute="_compute_amount_payment",
        store=True)
    payments_count = fields.Integer(
        string="Payments",
        compute="_compute_payments_count"
    )

    def _compute_currency(self):
        currency_id = self.env.company.currency_id
        for record in self:
            record.currency_id = currency_id

    def _compute_payments_count(self):
        account_payment = self.env['account.payment'].search([
            ("account_collective_payments_supplier_id", "=", self.id)
        ])
        for record in self:
            record.payments_count = len(account_payment)

    # Method show view
    def payments_view(self):
        self.ensure_one()
        domain = [
            ('account_collective_payments_supplier_id', '=', self.id)]
        return {
            'name': _('Payments'),
            'domain': domain,
            'res_model': 'account.payment',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
        }
