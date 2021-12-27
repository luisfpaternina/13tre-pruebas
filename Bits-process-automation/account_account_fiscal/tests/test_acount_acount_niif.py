# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from odoo.fields import Date
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestAcountAcountNiif(TransactionCase):

    def setUp(self):
        super(TestAcountAcountNiif, self).setUp()
        self.account_account = self.env['account.account']
        self.account_type = self.env['account.account.type']

        self.account_type1 = self.account_type.search([])
        self.account_account1 = self.account_account.new({
            'code': '11100011101',
            'name': 'Test Acount 1',
            'user_type_id': self.account_type1[0],
            'fiscal': False,
        })
        self.account_account2 = self.account_account.new({
            'code': '11100011100',
            'name': 'Test Acount 2',
            'user_type_id': self.account_type1[0],
            'fiscal': False,
        })
        self.account_account2.write({
            'fiscal': True,
            'homologation_account_fiscal_id': self.account_account1
        })
        self.account_account1.write({
            'fiscal': False,
            'homologation_account_fiscal_id': self.account_account2
        })

    def test_use_homologation(self):
        self.account_account2._onchange_homologation_fiscal()
        self.account_account1._onchange_homologation_fiscal()

    def test_use_homologation_witout_account_fiscal(self):
        self.account_account1.write({
            'fiscal': True
        })
        self.account_account1._onchange_homologation_fiscal()
