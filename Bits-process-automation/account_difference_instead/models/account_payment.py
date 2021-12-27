# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.modules.module import get_module_resource
from datetime import datetime


class AccountPyment(models.Model):
    _inherit = 'account.payment'

    vendors_account = ""
    expenses_account = ""
    income_account = ""
    unrealized_exchange_journal = ""

    def post(self):
        res = super(AccountPyment, self).post()
        for record in self:
            record.validate_type()
            record.expenses_account = self.get_config_value(
                "unrealized_exchange_expenses")
            record.income_account = self.get_config_value(
                "unrealized_exchange_income")
            record.unrealized_exchange_journal = self.get_config_value(
                "unrealized_exchange_journal")

            if(record.vendors_account and record.expenses_account and
               record.income_account and record.unrealized_exchange_journal):

                for invoice in record.reconciled_invoice_ids:
                    move_lines = self.env["account.move.line"].search([
                        ("bill_id.id", "=", invoice.id),
                        ("account_id", "=", record.vendors_account.id),
                    ])
                    total = 0
                    for move_line in move_lines:
                        total += move_line.debit - move_line.credit

                    communication = record.communication\
                        if record.communication else ""

                    journal_entry = self.env["account.move"].create({
                        'ref': communication + "/" + record.currency_id.name +
                        _('/UNREALIZED_EXCHANGE_RATE_CANCELLATION/(') +
                        datetime.now().strftime('%Y-%m-%d') + ')',
                        'journal_id': record.unrealized_exchange_journal.id
                    })
                    record.create_journal_items(
                        invoice.id, journal_entry, total)
                    journal_entry.action_post()

    def get_config_value(self, name):
        _parameter_value = self.env['ir.config_parameter'].sudo()
        account_id = _parameter_value.get_param(
            'account_difference_instead.' + name)
        account = self.env['account.account'].browse(int(account_id))
        return account

    def create_journal_items(self, bill_id, journal_entry, total):
        if(total < 0):
            self.env['account.move.line'].create([
                {
                    'account_id': self.vendors_account.id,
                    'debit': abs(total),
                    'bill_id': bill_id,
                    'move_id': journal_entry.id,
                    'partner_id': self.partner_id.id,
                    'name': self.communication
                },
                {
                    'account_id': self.income_account.id,
                    'credit': abs(total),
                    'bill_id': bill_id,
                    'move_id': journal_entry.id,
                    'partner_id': self.partner_id.id,
                    'name': self.communication
                }
            ])
        else:
            self.env['account.move.line'].create([
                {
                    'account_id': self.vendors_account.id,
                    'credit': total,
                    'bill_id': bill_id,
                    'move_id': journal_entry.id,
                    'partner_id': self.partner_id.id,
                    'name': self.communication
                },
                {
                    'account_id': self.expenses_account.id,
                    'debit': total,
                    'bill_id': bill_id,
                    'move_id': journal_entry.id,
                    'partner_id': self.partner_id.id,
                    'name': self.communication
                }
            ])
        return False

    def validate_type(self):
        if self.payment_type == "inbound":
            self.vendors_account = self.get_config_value(
                "unrealized_exchange_customers")
        else:
            self.vendors_account = self.get_config_value(
                "unrealized_exchange_vendors")
