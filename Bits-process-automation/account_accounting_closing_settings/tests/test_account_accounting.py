from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError, UserError
from odoo.tests.common import TransactionCase

# Review SavePoint implementation and SingleTransaction


class TestAccountAccounting(TransactionCase):

    def setUp(self):
        super(TestAccountAccounting, self).setUp()
        self.account_account = self.env['account.account']
        self.account_type = self.env['account.account.type']
        self.account_fiscal_year = self.env['account.fiscal.year']
        self.account_move = self.env['account.move']
        self.account_journal = self.env['account.journal']
        self.res_partner = self.env['res.partner']
        self.product_product = self.env['product.product']
        self.product_category = self.env['product.category']

        self.account_type1 = self.account_type.search([])

        self.account_account1 = self.account_account.new({
            'code': '1',
            'name': 'Test Acount 1',
            'user_type_id': self.account_type1[0],
        })
        self.account_account12 = self.account_account.new({
            'code': '12',
            'name': 'Test Acount 12',
            'user_type_id': self.account_type1[0],
        })
        self.account_account4 = self.account_account.new({
            'code': '4',
            'name': 'Test Acount 4',
            'user_type_id': self.account_type1[0],
        })
        self.account_account42 = self.account_account.new({
            'code': '42',
            'name': 'Test Acount 4',
            'user_type_id': self.account_type1[0],
        })
        self.account_account5 = self.account_account.new({
            'code': '5',
            'name': 'Test Acount 5',
            'user_type_id': self.account_type1[0],
        })
        self.account_account52 = self.account_account.new({
            'code': '5',
            'name': 'Test Acount 5',
            'user_type_id': self.account_type1[0],
        })
        self.account_account6 = self.account_account.new({
            'code': '6',
            'name': 'Test Acount 6',
            'user_type_id': self.account_type1[0],
        })
        self.account_account6 = self.account_account.new({
            'code': '62',
            'name': 'Test Acount 6',
            'user_type_id': self.account_type1[0],
        })
        self.account_account7 = self.account_account.new({
            'code': '7',
            'name': 'Test Acount 7',
            'user_type_id': self.account_type1[0],
        })
        self.account_account72 = self.account_account.new({
            'code': '72',
            'name': 'Test Acount 72',
            'user_type_id': self.account_type1[0],
        })

        # Test functionality
        self.partner = self.res_partner.create({
            'name': 'partner name'
        })
        self.liquidity_type_id = self.env.ref(
            'account.data_account_type_liquidity')
        self.account_bank = self.account_account.search(
            [('user_type_id', '=', self.liquidity_type_id.id)])
        self.journal_bank = self.account_journal.create({
            "name": "Test Bank",
            "code": "TESB",
            "type": "bank",
            'default_credit_account_id': self.account_bank[0].id,
            'default_debit_account_id':  self.account_bank[0].id
        })
        self.account_journal_1 = self.account_journal.create({
            "name": "Test",
            "code": "TEST1",
            "type": "purchase"
        })
        self.category_one = self.product_category.create({
            'name': 'All',
        })
        self.product_one = self.product_product.create({
            'name': 'product one',
            'categ_id': self.category_one.id,
            'type': 'consu',
            'lst_price': 10,
            'standard_price': 8,
            'sale_ok': True,
            'purchase_ok': True
        })
        self.account_1 = self.account_account.create({
            'name': 'Test Account 1',
            'code': '51236877',
            'reconcile': True,
            'user_type_id': self.env.ref(
                'account.data_account_type_payable').id,
            'allows_accounting_closing': True
        })
        self.account_2 = self.account_account.create({
            'name': 'Test Account 2',
            'code': '51236883',
            'user_type_id': self.env.ref(
                'account.data_account_type_liquidity').id,
            'allows_accounting_closing': True
        })
        self.account_3 = self.account_account.create({
            'name': 'Test Account 1',
            'code': '51236887',
            'user_type_id': self.env.ref(
                'account.data_account_type_current_assets').id
        })
        self.move_1 = self.account_move.create({
            'journal_id': self.journal_bank.id,
            'date': date(2021, 5, 4),
            'type': 'entry',
            'line_ids': [(0, 0, {
                'account_id': self.account_2.id,
                'partner_id': self.partner.id,
                'date': date(2021, 5, 4),
                'credit': 0.0,
                'debit': 1000.0
            }), (0, 0, {
                'account_id': self.account_1.id,
                'partner_id': self.partner.id,
                'date': date(2021, 5, 4),
                'credit': 1000.0,
                'debit': 0.0
            })]
        })
        self.move_1.post()
        self.account_fiscal_year_1 = self.account_fiscal_year.create({
            'name': 'Fiscal Year Test',
            'date_from': date(2021, 1, 1),
            'date_to': date(2021, 12, 31),
            'company_id': self.env['res.company'].search([])[0].id,
            'journal': self.journal_bank.id,
            'profit_account_year':
                self.env['account.account'].search([])[0].id,
            'account_lost_year':
                self.env['account.account'].search([])[1].id,
            'reference': 'Fiscal year reference',
        })

    def test_write_account_validation_on(self):
        account_account_100 = self.account_account.new({
            'code': '100',
            'name': 'Test Acount 100',
            'user_type_id': self.env.ref(
                'account.data_account_type_payable').id,
        })
        account_account_100._onchange_code()
        account_account_100.write({
            'code': "456",
        })

    def test_write_account_validation_off(self):
        account_account_200 = self.account_account.new({
            'code': '700',
            'name': 'Test Acount 700',
            'user_type_id': self.env.ref(
                'account.data_account_type_payable').id,
        })
        account_account_200._onchange_code()
        account_account_200.write({
            'code': "123",
        })

    def test_write_account_validation_without_code(self):
        account_account_300 = self.account_account.new({
            'code': False,
            'name': 'Test Acount 700',
            'user_type_id': self.env.ref(
                'account.data_account_type_payable').id,
        })
        account_account_300._onchange_code()

    def test_create_write_account_account_false(self):
        account_account_400 = self.account_account.create({
            'code': '400',
            'name': 'Test Acount 400',
            'user_type_id': self.env.ref(
                'account.data_account_type_payable').id,
            'reconcile': True
        })

        account_account_400.write({'code': False})

    def test_create_account_account_false(self):
        account_account_500 = self.account_account.new({
            'code': False,
            'name': 'Test Acount 400',
            'user_type_id': self.env.ref(
                    'account.data_account_type_payable').id,
            'reconcile': True
        })
        account_account_500.write({'code': '790'})

    def test_execute_accounting_close(self):
        self.account_fiscal_year_1.execute_accounting_close()
        self.account_fiscal_year_1._compute_journal_items_count()
        self.account_fiscal_year_1.journal_items_view()

    def test_execute_accounting_close_greatest_credit(self):
        account_move_1 = self.account_move.create({
            "journal_id": self.account_journal_1.id,
            "partner_id": self.partner.id,
            "date": date(2021, 5, 4),
            'type': 'in_invoice',
            "invoice_line_ids": [(0, 0, {
                'product_id': self.product_one.id,
                'account_id': self.account_3.id,
                'quantity': 2.0,
                'price_unit': 1000000,
            })]
        })
        account_move_1.post()
        self.account_fiscal_year_1.execute_accounting_close()

    def test_write_account_validation_without_code_2(self):
        account_account_300 = self.account_account.create({
            'code': False,
            'name': 'Test Acount 700',
            'user_type_id': self.env.ref(
                'account.data_account_type_payable').id,
        })
        account_account_300._onchange_code()
