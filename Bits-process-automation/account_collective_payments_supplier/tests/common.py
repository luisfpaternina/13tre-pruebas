# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, date

from odoo.fields import Date
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestAccountCollectivePaymentsSupplierBase(TransactionCase):

    def setUp(self):
        super(TestAccountCollectivePaymentsSupplierBase, self).setUp()
        self.wizard_ref = self.env['account.collective.payments.wizard']
        self.account_account = self.env['account.account']
        self.account_move = self.env['account.move']
        self.ResPartner = self.env['res.partner']
        self.collective_supplier_payment = self.env[
            'account.collective.payments.supplier']

        self.contact = self.ResPartner.create({
            'name': 'partner name'
        })
        self.liquidity_type_id = self.env.ref(
            'account.data_account_type_liquidity')
        self.payable_type_id = self.env.ref(
            'account.data_account_type_payable')
        self.payment_method = self.env.ref(
            'account_collective_payments.'
            'account_payment_method_electronic_out')
        self.company_id = self.env['res.company'].search([])
        self.account_payment = self.env['account.payment']
        self.currency_id = self.env['res.currency'].search([
            ('name', '=', 'USD')])
        self.account_bank = self.account_account.search(
            [('user_type_id', '=', self.liquidity_type_id.id)])

        self.journal_id = self.env['account.journal'].create({
            "name": "Test",
            "code": "TEST",
            "type": "general"
        })
        self.journal_purchase = self.env['account.journal'].create({
            "name": "Test Purchase",
            "code": "TESP",
            "type": "purchase",
            'default_credit_account_id': self.account_bank[0].id,
            'default_debit_account_id':  self.account_bank[0].id
        })
        self.account_id = self.env['account.account'].search(
            [('code', '=', '630000')], limit=1)
        self.partner_id = self.ref('base.res_partner_2')
        self.bank_id = self.env['res.bank'].search([])

        self.account_1 = self.account_account.create({
            'name': 'Test Account 1',
            'code': '51236877',
            'reconcile': True,
            'user_type_id': self.env.ref(
                'account.data_account_type_payable').id
        })
        self.account_2 = self.account_account.create({
            'name': 'Test Account 2',
            'code': '51236883',
            'user_type_id': self.env.ref(
                'account.data_account_type_liquidity').id
        })

        self.move_1 = self.account_move.create({
            'journal_id': self.journal_purchase.id,
            'partner_id': self.contact.id,
            'date': date(2020, 5, 4),
            'type': 'in_invoice',
            'line_ids': [(0, 0, {
                'account_id': self.account_2.id,
                'partner_id': self.contact.id,
                'journal_id': self.journal_purchase.id,
                'date': date(2020, 5, 4),
                'credit': 0.0,
                'debit': 1000.0
            }), (0, 0, {
                'account_id': self.account_1.id,
                'partner_id': self.contact.id,
                'journal_id': self.journal_purchase.id,
                'date': date(2020, 5, 4),
                'credit': 1000.0,
                'debit': 0.0
            })]
        })

        self.move_2 = self.account_move.create({
            'journal_id': self.journal_purchase.id,
            'partner_id': self.contact.id,
            'date': date(2020, 5, 4),
            'type': 'in_invoice',
            'line_ids': [(0, 0, {
                'account_id': self.account_2.id,
                'partner_id': self.contact.id,
                'journal_id': self.journal_purchase.id,
                'date': date(2020, 5, 4),
                'credit': 0.0,
                'debit': 1000.0
            }), (0, 0, {
                'account_id': self.account_1.id,
                'partner_id': self.contact.id,
                'journal_id': self.journal_purchase.id,
                'date': date(2020, 5, 4),
                'credit': 1000.0,
                'debit': 0.0
            })]
        })

        self.move_1.post()
        self.move_2.post()
