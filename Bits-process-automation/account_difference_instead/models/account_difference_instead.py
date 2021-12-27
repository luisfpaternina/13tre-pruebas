# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.modules.module import get_module_resource


class AccountDifferenceInstead(models.Model):
    _inherit = 'account.move'

    vendors_account = ""
    expenses_account = ""
    income_account = ""
    unrealized_exchange_journal = ""

    def _cron_execute_unrealized_exchange_difference(self):

        self.expenses_account = self.get_config_value(
            "unrealized_exchange_expenses")
        self.income_account = self.get_config_value(
            "unrealized_exchange_income")
        self.unrealized_exchange_journal = self.get_config_value(
            "unrealized_exchange_journal")
        self.vendors_account = self.get_config_value(
            "unrealized_exchange_vendors")

        if(self.expenses_account and self.income_account and
           self.unrealized_exchange_journal):
            main_currency = self.vendors_account.company_id.currency_id
            account_moves = self.get_necessary_account_move(main_currency)
            self.create_journal_entries(account_moves)

        return False

    def get_config_value(self, name):
        _parameter_value = self.env['ir.config_parameter'].sudo()
        account_id = _parameter_value.get_param(
            'account_difference_instead.' + name)
        account = self.env['account.account'].browse(int(account_id))
        return account

    def get_necessary_account_move(self, main_currency):
        account_moves = self.env['account.move'].search([
            ('state', '=', 'posted'),
            ('currency_id', '!=', main_currency.id),
            '|',
            '&', ('amount_residual_signed', '<', 0),
            ('type', '=', 'in_invoice'),
            '&', ('amount_residual_signed', '>', 0),
            ('type', '=', 'out_invoice')
        ])
        diff_currencies = {}
        for account_move in account_moves:
            if(not diff_currencies.get(account_move.currency_id.name)):
                diff_currencies[account_move.currency_id.name] = []
            diff_currencies[account_move.currency_id.name].append(account_move)

        return diff_currencies

    def create_journal_entries(self, account_moves):
        for key, value in account_moves.items():
            journal_entry = self.create({
                'ref': (key + _('/UNREALIZED_EXCHANGE_RATE/(') +
                        datetime.now().strftime('%Y-%m-%d') + ')'),
                'journal_id': self.unrealized_exchange_journal.id
            })
            for account_move in value:
                self.validate_type(account_move)
                self.create_journal_items(account_move, journal_entry)
            journal_entry.action_post()

    def create_journal_items(self, account_move, journal_entry):
        exchange_rate = self.difference_calculator(account_move)
        if (exchange_rate < 0 and account_move.type == "in_invoice") or\
                (exchange_rate > 0 and account_move.type == "out_invoice"):
            self.env['account.move.line'].create([
                {
                    'account_id': self.vendors_account.id,
                    'debit': abs(exchange_rate),
                    'bill_id': account_move.id,
                    'move_id': journal_entry.id,
                    'partner_id': account_move.partner_id.id,
                    'name': account_move.name
                },
                {
                    'account_id': self.income_account.id,
                    'credit': abs(exchange_rate),
                    'bill_id': account_move.id,
                    'move_id': journal_entry.id,
                    'partner_id': account_move.partner_id.id,
                    'name': account_move.name
                }
            ])
        else:
            self.env['account.move.line'].create([
                {
                    'account_id': self.vendors_account.id,
                    'credit': abs(exchange_rate),
                    'bill_id': account_move.id,
                    'move_id': journal_entry.id,
                    'partner_id': account_move.partner_id.id,
                    'name': account_move.name
                },
                {
                    'account_id': self.expenses_account.id,
                    'debit': abs(exchange_rate),
                    'bill_id': account_move.id,
                    'move_id': journal_entry.id,
                    'partner_id': account_move.partner_id.id,
                    'name': account_move.name
                }
            ])

        return False

    def difference_calculator(self, account_move):
        currency_rate = self.get_specific_currency_rate(
            account_move.currency_id, datetime.now().date())
        old_currency_rate = self.get_specific_currency_rate(
            account_move.currency_id, account_move.invoice_date)

        old_exchange_rate = account_move.amount_total / old_currency_rate
        exchange_rate = account_move.amount_total / currency_rate

        journal_items = self.env['account.move.line'].search([
            ('bill_id', '=', account_move.id),
            ('account_id', '=', self.vendors_account.id)
        ])

        if(len(journal_items) > 0):
            for journal_item in journal_items:
                if account_move.type == "in_invoice":
                    old_exchange_rate = ((
                        old_exchange_rate - journal_item.debit)
                        if journal_item.debit else (
                        old_exchange_rate + journal_item.credit))
                else:
                    old_exchange_rate = ((
                        old_exchange_rate + journal_item.debit)
                        if journal_item.debit else (
                        old_exchange_rate - journal_item.credit))

        result = exchange_rate - old_exchange_rate
        return result

    def get_specific_currency_rate(self, currency, date):
        currency_rates = self.env["res.currency.rate"].search([
            ('currency_id', '=', currency.id)
        ], order='name asc')
        specific_currency_rate = ''
        for currency_rate in currency_rates:
            if date >= currency_rate.name:
                specific_currency_rate = currency_rate.rate
        return specific_currency_rate

    def validate_type(self, account_move):
        if account_move.type == "in_invoice":
            self.vendors_account = self.get_config_value(
                "unrealized_exchange_vendors")

        else:
            self.vendors_account = self.get_config_value(
                "unrealized_exchange_customers")
