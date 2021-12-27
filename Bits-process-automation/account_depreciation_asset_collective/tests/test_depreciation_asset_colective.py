from datetime import datetime, date
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestDepreciationAssetColective(TransactionCase):

    def setUp(self):
        super(TestDepreciationAssetColective, self).setUp()
        self.account_asset = self.env['account.asset']
        self.account_account = self.env['account.account']
        self.account_journal = self.env['account.journal']
        self.depreciation_asset_collective = self.env[
            'depreciation.asset.collective']
        self.asset_collective = self.depreciation_asset_collective.create({
            'assets_depreciate': 'all',
            'depreciation_date': date(2020, 7, 14)
        })
        self.account_1 = self.account_account.create({
            'name': 'Test Account 1',
            'code': '51236897',
            'user_type_id': self.env.ref(
                'account.data_account_type_current_assets').id
        })
        self.account_2 = self.account_account.create({
            'name': 'Test Account 2',
            'code': '51236883',
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
            'account_asset_id': self.account_1.id,
            'account_depreciation_id': self.account_1.id,
            'account_depreciation_expense_id': self.account_2.id,
            'journal_id': self.journal.id,
            'asset_type': 'sale',
            'asset_group': 'asset'
        })

        self.asset_intangible = self.account_asset.create({
            'name': "Tets asset",
            'first_depreciation_date': date(2020, 6, 30),
            'method_number': 5,
            'method_period': '1',
            'original_value': 3657000,
            'method': 'linear',
            'account_asset_id': self.account_1.id,
            'account_depreciation_id': self.account_1.id,
            'account_depreciation_expense_id': self.account_2.id,
            'journal_id': self.journal.id,
            'asset_type': 'sale',
            'asset_group': 'intangible'
        })

    def test_depreciation_asset(self):
        self.asset_asset.compute_depreciation_board()
        self.asset_asset.validate()

        self.asset_intangible.compute_depreciation_board()
        self.asset_intangible.validate()

        self.asset_collective.depreciation_asset()

        asset_move = self.env['account.move'].search(
            [('asset_id', '=', self.asset_asset.id),
             ('date', '<=', date(2020, 7, 14))])
        asset_intangible = self.env['account.move'].search(
            [('asset_id', '=', self.asset_intangible.id),
             ('date', '<=', date(2020, 7, 14))])
        self.assertEqual(len(asset_move+asset_intangible), 4)

    def test_depreciation_asset_not_all(self):
        self.asset_asset.compute_depreciation_board()
        self.asset_asset.validate()

        self.asset_collective.write({
            'assets_depreciate': 'asset'
        })
        self.asset_collective.depreciation_asset()

    def test_depreciation_asset_without_asset(self):
        self.asset_asset.unlink()
        self.asset_intangible.unlink()
        asset_collective = self.depreciation_asset_collective.create({
            'assets_depreciate': 'all',
            'depreciation_date': date(2020, 3, 31)
        })
        asset_collective.depreciation_asset()
