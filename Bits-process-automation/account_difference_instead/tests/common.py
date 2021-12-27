from datetime import datetime, date, timedelta
from odoo.fields import Date
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestAccountDifference(TransactionCase):

    def setUp(self):
        super(TestAccountDifference, self).setUp()

        self.account_account = self.env['account.account']
        self.account_move = self.env['account.move']
        self.res_partner = self.env['res.partner']
        self.Product = self.env['product.product']
        self.ProductCategory = self.env['product.category']
        self.AccountAccount = self.env['account.account']
        self.AccountPayment = self.env['account.payment']
        self.journal_bank = self.env['account.journal']
        self.company_id = self.env['res.company'].browse([1])
        self.res_cunrrency = self.env['res.currency'].search([])
        self.res_config_settings = self.env['res.config.settings'].create({})
        self.res_config_settings.group_multi_currency = True

        self.USD_money = self.env['res.currency'].search([
            ('name', '=', 'USD')
        ])
        self.company_id.write({
            'currency_id': self.USD_money.id
        })
        self.category_one = self.ProductCategory.create({
            'name': 'All',

        })

        self.product_one = self.Product.create({
            'name': 'product one',
            'categ_id': self.category_one.id,
            'type': 'consu',
            'lst_price': 10,
            'standard_price': 8,
            'sale_ok': True,
            'purchase_ok': True
        })

        self.account_recivable = self.account_account.create({
            'name': 'Test Account 1',
            'code': '51236869',
            'reconcile': True,
            'user_type_id': self.env.ref(
                'account.data_account_type_receivable').id,
            'company_id': self.company_id.id
        })
        self.account_payable = self.account_account.create({
            'name': 'Test Account 2',
            'code': '12568721',
            'reconcile': True,
            'user_type_id': self.env.ref(
                'account.data_account_type_payable').id,
            'company_id': self.company_id.id
        })

        self.partner = self.res_partner.create({
            'name': "Pepito Perez",
            'property_account_receivable_id': self.account_recivable.id,
            'property_account_payable_id': self.account_payable.id,
        })

        self.account_1 = self.account_account.create({
            'name': 'Test Account 1',
            'code': '51236897',
            'user_type_id': self.env.ref(
                'account.data_account_type_current_assets').id,
            'company_id': self.company_id.id
        })
        self.account_2 = self.account_account.create({
            'name': 'Test Account 2',
            'code': '51236883',
            'user_type_id': self.env.ref(
                'account.data_account_type_current_assets').id,
            'company_id': self.company_id.id
        })
        self.account_3 = self.account_account.create({
            'name': 'Test Account 3',
            'code': '51236884',
            'user_type_id': self.env.ref(
                'account.data_account_type_current_assets').id,
            'company_id': self.company_id.id
        })
        self.other_currency = self.env['res.currency'].search([
            ('name', '=', 'EUR')
        ])

        self.account_bank = self.account_account.create({
            'name': 'Test Account Bank',
            'code': '51236885',
            'user_type_id': self.env.ref(
                'account.data_account_type_liquidity').id,
            'company_id': self.company_id.id,
            'currency_id': self.other_currency.id
        })

        self.account_journal = self.env['account.journal'].create({
            "name": "Test",
            "code": "TEST",
            "type": "general",
            "currency_id": self.other_currency.id
        })
        self.account_journal_1 = self.env['account.journal'].create({
            "name": "Test",
            "code": "TEST1",
            "type": "purchase",
            "currency_id": self.company_id.currency_id.id
        })
        self.account_journal_2 = self.env['account.journal'].create({
            "name": "Test2",
            "code": "TEST2",
            "type": "purchase",
            "currency_id": self.company_id.currency_id.id
        })
        self.bank_journal = self.env['account.journal'].create({
            "name": "Testbank",
            "code": "TESTBANK",
            "type": "bank",
            "currency_id": self.other_currency.id,
            'default_credit_account_id': self.account_bank.id,
            'default_debit_account_id': self.account_bank.id
        })
        self.other_currency.write({
            "rate_ids": [(0, 0, {
                'name': date(2020, 2, 1),
                'rate': 1.0
            })]
        })
        self.account_move_0 = self.account_move.create({
            "journal_id": self.account_journal_1.id,
            "partner_id": self.partner.id,
            'invoice_date': '2020-01-01',
            'type': 'in_invoice',
            "line_ids": [(0, 0, {
                'account_id': self.account_3.id,
                'product_id': self.product_one.id,
                'partner_id': self.partner.id,
                'debit': 60000,
            }), (0, 0, {
                'account_id': self.account_payable.id,
                'product_id': self.product_one.id,
                'partner_id': self.partner.id,
                'credit': 60000,
            })],
            "invoice_line_ids": [(0, 0, {
                'product_id': self.product_one.id,
                'account_id': self.account_3.id,
                'quantity': 2.0,
                'price_unit': 30000,
            })]
        })
        self.account_move_0.post()

        self.account_move_1 = self.account_move.create({
            "currency_id": self.other_currency.id,
            "partner_id": self.partner.id,
            'invoice_date': '2020-01-01',
            'type': 'in_invoice',
            "invoice_line_ids": [(0, 0, {
                'product_id': self.product_one.id,
                'account_id': self.account_3.id,
                'quantity': 2.0,
                'price_unit': 25000,
            })]
        })
        self.account_move_1.post()

        self.account_move_2 = self.account_move.create({
            "currency_id": self.other_currency.id,
            "partner_id": self.partner.id,
            'type': 'in_invoice',
            "invoice_line_ids": [(0, 0, {
                'product_id': self.product_one.id,
                'account_id': self.account_3.id,
                'quantity': 2.0,
                'price_unit': 2000,
            })]
        })
        self.account_move_2.post()

        self.account_move_3 = self.account_move.create({
            "currency_id": self.other_currency.id,
            "partner_id": self.partner.id,
            "date": date(2020, 1, 1),
            'type': 'in_invoice',
            "invoice_line_ids": [(0, 0, {
                'product_id': self.product_one.id,
                'account_id': self.account_3.id,
                'quantity': 2.0,
                'price_unit': 1000,
            })]
        })
        self.account_move_3.post()

        self.account_move_4 = self.account_move.create({
            "journal_id": self.account_journal_1.id,
            "currency_id": self.other_currency.id,
            "partner_id": self.partner.id,
            "date": date(2020, 1, 1),
            'type': 'out_invoice',
            "invoice_line_ids": [(0, 0, {
                'product_id': self.product_one.id,
                'account_id': self.account_3.id,
                'quantity': 2.0,
                'price_unit': 1000,
            })]
        })
        self.account_move_4.post()

        self.account_move_5 = self.account_move.create({
            "journal_id": self.account_journal_1.id,
            "currency_id": self.other_currency.id,
            "partner_id": self.partner.id,
            "date": date(2020, 1, 1),
            'type': 'out_invoice',
            "invoice_line_ids": [(0, 0, {
                'product_id': self.product_one.id,
                'account_id': self.account_3.id,
                'quantity': 2.0,
                'price_unit': 1000,
            })]
        })
        self.account_move_5.post()

        self.account_bank = self.AccountAccount.create({
            'code': "10151206",
            'name': "TEST Account Bank",
            'create_asset': 'validate',
            'user_type_id': self.env.ref(
                'account.data_account_type_liquidity').id
        })

        self.account_payment = self.AccountPayment.create({
            'journal_id': self.bank_journal.id,
            'payment_type': "outbound",
            'partner_type': "supplier",
            'state': 'draft',
            'destination_account_id': self.account_bank,
            'communication': " ",
            'invoice_ids': [
                self.account_move_1.id
            ],
            'has_invoices': True,
            'payment_date': date(2020, 5, 30),
            'partner_id': self.partner.id,
            'amount': 10000.0,
            'currency_id': self.USD_money.id,
            'payment_method_id': self.env.ref(
                'account.account_payment_method_manual_out').id
        })

        self.account_payment2 = self.AccountPayment.create({
            'journal_id': self.bank_journal.id,
            'payment_type': "inbound",
            'partner_type': "supplier",
            'state': 'draft',
            'destination_account_id': self.account_bank,
            'communication': " ",
            'invoice_ids': [
                self.account_move_5.id
            ],
            'has_invoices': True,
            'payment_date': date(2020, 5, 30),
            'partner_id': self.partner.id,
            'amount': 10000.0,
            'currency_id': self.USD_money.id,
            'payment_method_id': self.env.ref(
                'account.account_payment_method_manual_out').id
        })

        payment_recordset = self.AccountPayment.search([])
        payment_recordset.post()
