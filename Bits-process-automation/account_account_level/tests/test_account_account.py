from datetime import datetime, timedelta, date
from odoo.exceptions import ValidationError, UserError
from odoo.tests.common import TransactionCase

# Review SavePoint implementation and SingleTransaction


class TestAccountAccount(TransactionCase):

    def setUp(self):
        super(TestAccountAccount, self).setUp()
        self.account_account = self.env['account.account']
        self.account_type = self.env['account.account.type']

        self.account_type1 = self.account_type.search([])

        self.account_account1 = self.account_account.new({
            'code': '1',
            'name': 'Test Acount 1',
            'user_type_id': self.account_type1[0],
            'level': '1'
        })
        self.account_account2 = self.account_account.new({
            'code': '12',
            'name': 'Test Acount 12',
            'user_type_id': self.account_type1[1],
            'level': '2',
            'depends_on': self.account_account1.id
        })
        self.account_account3 = self.account_account.new({
            'code': '1205',
            'name': 'Test Acount 1205',
            'user_type_id': self.account_type1[2],
            'level': '3',
            'depends_on': self.account_account2.id
        })
        self.account_account4 = self.account_account.new({
            'code': '120505',
            'name': 'Test Acount 120505',
            'user_type_id': self.account_type1[0],
            'level': '4',
            'depends_on': self.account_account3.id
        })
        self.account_account5 = self.account_account.new({
            'code': '12050505',
            'name': 'Test Acount 12050505',
            'user_type_id': self.account_type1[0],
            'level': '5',
            'depends_on': self.account_account4.id
        })
        self.account_account6 = self.account_account.new({
            'code': '1205050505',
            'name': 'Test Acount 1205050505',
            'user_type_id': self.account_type1[0],
            'level': '6',
            'depends_on': self.account_account5.id
        })
        self.account_account7 = self.account_account.new({
            'code': '120505050505',
            'name': 'Test Acount 120505050505',
            'user_type_id': self.account_type1[0],
            'level': '7',
            'depends_on': self.account_account6.id
        })
        self.account_account8 = self.account_account.new({
            'code': '120505050506',
            'name': 'Test Acount 120505050506',
            'user_type_id': self.account_type1[0],
            'level': '7',
            'depends_on': self.account_account6.id
        })

    def test_use_level(self):
        self.account_account7._onchange_level()
        self.account_account7._onchange_depends_on()
        self.account_account8._onchange_level()
        self.account_account8._onchange_depends_on()

    def test_use_level_validation(self):
        with self.assertRaises(ValidationError):
            self.account_account8.write({
                'level': '1',
                'code': '20'
            })
            self.account_account8._onchange_level()

    def test_use_level_false(self):
        self.account_account9 = self.account_account.new({
            'code': '120505050504',
            'name': 'Test Acount 120505050504',
            'user_type_id': self.account_type1[0],
            'level': False
        })

    def test_use_level_dependency_validation(self):
        with self.assertRaises(ValidationError):
            self.account_account8.write({
                'depends_on': self.account_account7.id
            })
            self.account_account8._onchange_depends_on()

    def test_create_account(self):
        self.account_account.create({
            'code': '12050505',
            'name': 'Test Acount 12050505',
            'user_type_id': self.env.ref(
                'account.data_account_type_payable').id,
            'level': '5',
            'depends_on': self.account_account4.id,
            'reconcile': True
        })

    def test_create_account_not_level(self):
        account_account_1 = self.account_account.create({
            'code': '120505',
            'name': 'Test Acount 120505',
            'user_type_id': self.env.ref(
                'account.data_account_type_payable').id,
            'level': '4',
            'depends_on': self.account_account3.id,
            'reconcile': True
        })
        account_account_2 = self.account_account.create({
            'code': '12050505',
            'name': 'Test Acount 12050505',
            'user_type_id': self.env.ref(
                'account.data_account_type_payable').id,
            'depends_on': account_account_1.id,
            'reconcile': True
        })
        with self.assertRaises(ValidationError):
            account_account_2.write({
                'level': '5',
                'depends_on': account_account_1.id,
                'code': '1205050'
            })

    def test_write_account_validation(self):
        account_account_1 = self.account_account.new({
            'name': 'Test Acount 1',
            'user_type_id': self.env.ref(
                'account.data_account_type_payable').id,
            'level': '1',
            'reconcile': True
        })
        account_account_1._onchange_level()
        account_account_1_1 = self.account_account.create({
            'code': '2',
            'name': 'Test Acount 2',
            'user_type_id': self.env.ref(
                'account.data_account_type_payable').id,
            'level': '1',
            'reconcile': True
        })
        account_account_2 = self.account_account.create({
            'code': '12',
            'name': 'Test Acount 12',
            'user_type_id': self.env.ref(
                'account.data_account_type_payable').id,
            'reconcile': True
        })
        account_account_2._onchange_depends_on()
        account_account_2.write({
            'code': "23",
            'depends_on': account_account_1_1.id,
            'level': '2'
        })
