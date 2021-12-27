from datetime import datetime, date
from odoo import api, fields, models, _
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError


class TestAccountAssetColgap(TransactionCase):

    def setUp(self):
        super(TestAccountAssetColgap, self).setUp()
        self.account_asset = self.env['account.asset']
        self.account_account = self.env['account.account']
        self.account_journal = self.env['account.journal']
        self.reverse_moves = self.env['account.move.reversal']
        self.asset_sell = self.env['account.asset.sell']
        self.account_move = self.env['account.move']
        self.reverse = self.reverse_moves.create({
            'date': date(2020, 4, 30)
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
        self.account_3 = self.account_account.create({
            'name': 'Test Account 1',
            'code': '51236887',
            'user_type_id': self.env.ref(
                'account.data_account_type_current_assets').id
        })
        self.account_4 = self.account_account.create({
            'name': 'Test Account 2',
            'code': '51236893',
            'user_type_id': self.env.ref(
                'account.data_account_type_current_assets').id
        })
        self.journal = self.account_journal.create({
            'name': 'Test Journal',
            'type': 'general',
            'code': 'TSTJ1'
        })
        self.journal_colgap = self.account_journal.create({
            'name': 'Test Journal colgap',
            'type': 'general',
            'code': 'TSTJ1'
        })
        self.asset_asset = self.account_asset.create({
            'name': "Tets asset",
            'first_depreciation_date': date(2020, 4, 30),
            'method_number': 5,
            'method_number_colgap': 10,
            'method_period': '1',
            'method_period_colgap': '1',
            'original_value': 3657000,
            'method': 'linear',
            'method_colgap': 'linear',
            'account_asset_id': self.account_1.id,
            'account_depreciation_id': self.account_1.id,
            'account_depreciation_expense_id': self.account_2.id,
            'account_asset_colgap_id': self.account_3.id,
            'account_depreciation_colgap_id': self.account_3.id,
            'account_depreciation_expense_colgap_id': self.account_4.id,
            'journal_id': self.journal.id,
            'journal_colgap_id': self.journal_colgap.id,
            'asset_type': 'sale',
        })

        self.asset_intangible = self.account_asset.create({
            'name': "Tets asset",
            'first_depreciation_date': date(2020, 6, 30),
            'method_number': 5,
            'method_number_colgap': 10,
            'method_period': '1',
            'method_period_colgap': '1',
            'original_value': 3657000,
            'method': 'linear',
            'account_asset_id': self.account_1.id,
            'account_depreciation_id': self.account_1.id,
            'account_depreciation_expense_id': self.account_2.id,
            'account_asset_colgap_id': self.account_3.id,
            'account_depreciation_colgap_id': self.account_3.id,
            'account_depreciation_expense_colgap_id': self.account_4.id,
            'journal_id': self.journal.id,
            'journal_colgap_id': self.journal_colgap.id,
            'asset_type': 'sale',
        })

    def test_validate(self):
        self.asset_asset.validate()
        if (self.asset_asset.depreciation_move_ids and
                self.asset_asset.depreciation_move_colgap_ids):
            self.asset_asset.validate()

    def test_compute_depreciation_board(self):
        self.asset_intangible.compute_depreciation_board()
        if (self.asset_intangible.depreciation_move_ids and
                self.asset_intangible.depreciation_move_colgap_ids):
            self.asset_intangible.compute_depreciation_board()

    def test_amount_change_colgap_ids(self):
        self.asset_asset.validate()
        move_select = False
        for move in self.asset_asset.depreciation_move_colgap_ids:
            if move.date < fields.Date.today():
                move_select = move
                break
        move_select.post()

    def test_amount_with_prorata(self):
        self.asset_asset.write({
            'prorata': True,
            'prorata_date': date(2020, 4, 30)
        })
        self.asset_asset.validate()

    def test_amount_with_year(self):
        self.asset_asset.write({
            'prorata': True,
            'prorata_date': date(2020, 4, 30),
            'method_period_colgap': '12'
        })
        self.asset_asset.validate()

    def test_amount_with_negative_original_value(self):
        self.asset_asset.write({
            'original_value': -3657000
        })
        self.asset_asset.validate()

    def test_onchange_account_asset_colgap_id(self):
        self.asset_asset.validate()
        self.asset_asset._onchange_account_asset_colgap_id()

    def test_purchase_onchange_account_asset_colgap_id(self):
        self.asset_asset.write({
            'asset_type': 'purchase'
        })
        self.asset_asset.validate()
        self.asset_asset._onchange_account_asset_colgap_id()

    def test_onchange_salvage_value_colgap(self):
        self.asset_asset.validate()
        self.asset_asset._onchange_salvage_value_colgap()

    def test_compute_board_amount_colgap(self):
        self.asset_asset.write({
            'method_colgap': 'degressive',
        })
        self.asset_asset.validate()

    def test_degressive_then_linear(self):
        self.asset_asset.write({
            'method_colgap': 'degressive_then_linear',
        })
        self.asset_asset.validate()

    def test_original_move_line_ids(self):
        self.asset_asset.compute_depreciation_board()
        move_select = False
        for move in self.asset_asset.depreciation_move_colgap_ids:
            if move.date < fields.Date.today():
                move_select = move
                break
        for move in move_select.line_ids:
            move.write({
                'asset_id': self.asset_asset.id
            })
        self.asset_asset.validate()

    def test_posted_depreciation_move_colgap(self):
        self.asset_asset.compute_depreciation_board()
        move_select = False
        for move in self.asset_asset.depreciation_move_colgap_ids:
            if move.date < fields.Date.today():
                move_select = move
                break
        self.asset_asset.validate()
        move_select.post()
        self.asset_asset.set_to_draft()
        self.asset_asset.compute_depreciation_board()

    def test_validation_credit_amount(self):
        self.asset_asset.validation_credit_amount(0.0, 0.0)

    def test_amount_to_depreciate_colgap(self):
        self.asset_asset.write({
            'first_depreciation_date': date(2020, 1, 30)
        })
        self.asset_asset.compute_depreciation_board()
        self.asset_asset.validate()
        for move in self.asset_asset.depreciation_move_colgap_ids:
            move.post()
        self.asset_asset.set_to_draft()
        self.asset_asset.compute_depreciation_board()

    def test_amount_change_colgap(self):
        self.asset_asset.compute_depreciation_board()
        move_select = False
        for move in self.asset_asset.depreciation_move_colgap_ids:
            if move.date < fields.Date.today():
                move_select = move
                break
        self.asset_asset.validate()
        move_select.write({
            'asset_value_change': True
        })
        move_select.post()
        self.asset_asset.set_to_draft()
        self.asset_asset.compute_depreciation_board()

    def test_reversal_move(self):
        self.asset_asset.compute_depreciation_board()
        self.asset_asset.validate()
        for i, move in enumerate(
                self.asset_asset.depreciation_move_colgap_ids):
            if i < len(self.asset_asset.depreciation_move_colgap_ids):
                move.write({
                    'asset_value_change': True
                })
                move.post()
                move._reverse_moves()
        self.reverse.with_context(
            active_ids=self.asset_asset.depreciation_move_colgap_ids.ids
        ).reverse_moves()
        self.asset_asset.set_to_draft()
        self.asset_asset.compute_depreciation_board()

    def test_depreciate_not_colgap(self):
        self.asset_asset.compute_depreciation_board()
        self.asset_asset.validate()
        for move in self.asset_asset.depreciation_move_ids:
            move.post()

    def test_depreciate_asset_close(self):
        self.asset_asset.compute_depreciation_board()
        self.asset_asset.validate()
        self.sell = self.asset_sell.create({
            'action': 'dispose',
            'loss_account_id': self.account_1.id,
            'asset_id': self.asset_asset.id
        })
        self.sell.do_action()
        for move in self.asset_asset.depreciation_move_ids:
            move.post()
        for move in self.asset_asset.depreciation_move_colgap_ids:
            move.post()

    def test_depreciate_asset_draft(self):
        self.asset_asset.compute_depreciation_board()
        for move in self.asset_asset.depreciation_move_ids:
            with self.assertRaises(UserError):
                move.post()
        for move in self.asset_asset.depreciation_move_colgap_ids:
            with self.assertRaises(UserError):
                move.post()

    def test_compute_board_amount_niif(self):
        self.asset_asset.write({
            'method': 'degressive',
        })
        self.asset_asset.validate()

    def test_depreciate_all_moves(self):
        self.asset_asset._recompute_board_colgap(
            0, 0, 200, '2020-04-30', 0, self.account_move)

    def test_amount_change_colgap_not_entry(self):
        self.asset_asset.compute_depreciation_board()
        self.asset_asset.validate()
        for i, move in enumerate(
                self.asset_asset.depreciation_move_colgap_ids):
            if i < len(self.asset_asset.depreciation_move_colgap_ids):
                move.post()
                move._reverse_moves()
        self.reverse.with_context(
            active_ids=self.asset_asset.depreciation_move_colgap_ids.ids
        ).reverse_moves()
        self.asset_asset.set_to_draft()
        self.asset_asset.compute_depreciation_board()
