from datetime import datetime, date, timedelta
from odoo.fields import Date
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestAccountStatement(TransactionCase):

    def setUp(self):
        super(TestAccountStatement, self).setUp()
        self.account_journal = self.env["account.journal"]
        self.account_account = self.env["account.account"]
        self.account_bank_statement = self.env["account.bank.statement"]
        self.reconciliation_widget = self.env["account.reconciliation.widget"]
        self.res_config_settings = self.env["res.config.settings"]

        self.account_1 = self.account_account.create({
            'name': 'Test Account 1',
            'code': '51236877',
            'reconcile': True,
            'create_asset': 'draft',
            'user_type_id': self.env.ref(
                'account.data_account_type_payable').id
        })
        self.account_journal_1 = self.account_journal.create({
            "name": "Bank Test",
            "code": "BT",
            "type": "bank",
            'default_credit_account_id': self.account_1.id,
            'default_debit_account_id':  self.account_1.id
        })
        self.account_bank_statement_1 = self.account_bank_statement.create({
            "journal_id": self.account_journal_1.id,
            "date": "2021-04-02",
            "line_ids": [(0, 0, {
                "date": "2021-04-02",
                "name": "4XMIL GRAVAMEN",
                "amount": 200000,
                "journal_id": self.account_journal_1.id
            })]
        })
