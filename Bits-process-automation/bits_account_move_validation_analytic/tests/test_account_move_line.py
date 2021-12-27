from datetime import datetime, timedelta, date

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestAccountMoveLine(TransactionCase):

    def setUp(self):
        super(TestAccountMoveLine, self).setUp()
        self.account_asset = self.env['account.asset']
        self.AccountAccount = self.env['account.account']
        self.AccountAccountType = self.env['account.account.type']
        self.AccountJournal = self.env['account.journal']
        self.account_journal = self.env['account.journal']

        self.account_id = self.env['account.account'].create({
            'name': 'Neutral Account',
            'code': 'NEUT',
            'user_type_id': self.env.ref(
                'account.data_account_type_current_assets').id
        })

        self.journal = self.account_journal.create({
            'name': 'Test Journal',
            'type': 'general',
            'code': 'TSTJ1'
        })

        self.asset_asset = self.account_asset.create({
            'name': "Tets asset",
            'first_depreciation_date': date(2020, 4, 30),
            'method_number': 5,
            'method_period': '1',
            'original_value': 3657000,
            'method': 'linear',
            'account_asset_id': self.account_id.id,
            'account_depreciation_id': self.account_id.id,
            'journal_id': self.journal.id,
            'asset_type': 'sale',
            'asset_group': 'asset'
        })

        self.analytic_id = self.env['account.analytic.account'].create({
            'name': 'TEST',
            'code': '0001'
        })

        self.account_journal = self.AccountJournal.create({
            'name': 'account journal test',
            'code': 'NOM',
            'type': 'general'
        })

        self.account_move = self.env['account.move'].create({
            'ref': 'Nomina Test',
            'date': datetime.now(),
            'journal_id': self.account_journal.id
        })

    def test_check_analytic_account_id_required(self):
        record = self.env["account.move.line"].new({
            'account_id': self.account_id.id,
            'analytic_account_id': self.analytic_id.id,
        })
        record._check_analytic_account_id_required()

        config = self.env['res.config.settings'].create({})
        config.user_type_ids = [self.account_id.user_type_id.id]
        config.execute()

        with self.assertRaises(ValidationError):
            record = self.env["account.move.line"].create([
                {
                    'account_id': self.account_id.id,
                    'analytic_account_id': self.analytic_id.id,
                    'move_id': self.account_move.id
                },
                {
                    'account_id': self.account_id.id,
                    'analytic_account_id': False,
                    'move_id': self.account_move.id
                }
            ])
