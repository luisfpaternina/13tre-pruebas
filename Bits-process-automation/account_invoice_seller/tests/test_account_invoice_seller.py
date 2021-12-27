from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError, UserError
from odoo.tests.common import TransactionCase


class TestAccountInvoiceSeller(TransactionCase):

    def setUp(self):
        super(TestAccountInvoiceSeller, self).setUp()
        self.account_account = self.env['account.account']
        self.account_move = self.env['account.move']
        self.ResPartner = self.env['res.partner']

        self.contact = self.ResPartner.create({
            'name': 'partner name'
        })
        self.liquidity_type_id = self.env.ref(
            'account.data_account_type_liquidity')
        self.payable_type_id = self.env.ref(
            'account.data_account_type_payable')
        self.company_id = self.env['res.company'].search([])
        self.account_payment = self.env['account.payment']
        self.other_currency = self.env['res.currency'].search([
            ('name', '=', 'EUR')])
        self.other_currency_1 = self.env['res.currency'].search([
            ('name', '=', 'USD')])
        self.account_bank = self.account_account.search(
            [('user_type_id', '=', self.liquidity_type_id.id)])

        self.journal_id = self.env['account.journal'].create({
            "name": "Test",
            "code": "TEST",
            "type": "general"
        })
        self.journal_sale = self.env['account.journal'].create({
            "name": "Test Bank",
            "code": "TESB",
            "type": "sale",
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

    def test_onchange_partner_user_commercial(self):
        move_1 = self.account_move.create({
            'journal_id': self.journal_sale.id,
            'date': date(2020, 5, 4),
            'type': 'out_invoice'
        })
        move_1._onchange_partner_user_commercial()

    def test_onchange_partner_user_co_partner(self):
        move_1 = self.account_move.new({
            'journal_id': self.journal_sale.id,
            'date': date(2020, 5, 4),
            'type': 'out_invoice',
            'partner_id': self.contact.id
        })
        with self.assertRaises(ValidationError):
            move_1._onchange_partner_user_commercial()

    def test_onchange_partner_user_co_seller(self):
        self.contact.write({
            'user_id': self.env.user.id
        })
        move_1 = self.account_move.new({
            'journal_id': self.journal_sale.id,
            'date': date(2020, 5, 4),
            'type': 'out_invoice',
            'partner_id': self.contact.id
        })
        move_1._onchange_partner_user_commercial()

    def test_create_invoice_with_out_partner(self):
        with self.assertRaises(ValidationError):
            self.account_move.with_context(
                default_type='out_invoice').create({
                    'journal_id': self.journal_sale.id,
                    'date': date(2020, 5, 4),
                    'type': 'out_invoice'
                })

    def test_create_invoice_with_partner(self):
        with self.assertRaises(ValidationError):
            self.account_move.with_context(
                default_type='out_invoice').create({
                    'journal_id': self.journal_sale.id,
                    'date': date(2020, 5, 4),
                    'type': 'out_invoice',
                    'partner_id': self.contact.id
                })

    def test_create_invoice_with_selller(self):
        self.contact.write({
            'user_id': self.env.user.id
        })
        self.account_move.with_context(
            default_type='out_invoice').create({
                'journal_id': self.journal_sale.id,
                'date': date(2020, 5, 4),
                'type': 'out_invoice',
                'partner_id': self.contact.id
            })
