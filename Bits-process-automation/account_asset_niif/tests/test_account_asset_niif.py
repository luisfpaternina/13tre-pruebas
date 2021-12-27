from datetime import datetime, date
from odoo import api, fields, models, _
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError


class TestAccountAssetNiif(TransactionCase):

    def setUp(self):
        super(TestAccountAssetNiif, self).setUp()
        self.account_asset = self.env['account.asset']
        self.account_account = self.env['account.account']
        self.account_journal = self.env['account.journal']
        self.reverse_moves = self.env['account.move.reversal']
        self.asset_sell = self.env['account.asset.sell']
        self.account_move = self.env['account.move']
        self.res_partner = self.env['res.partner']
        self.product_product = self.env['product.product']
        self.product_category = self.env['product.category']
        self.company_id = self.env['res.company'].browse([1])
        self.res_cunrrency = self.env['res.currency'].search([])[0]
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
        self.account_journal_1 = self.env['account.journal'].create({
            "name": "Test",
            "code": "TEST1",
            "type": "sale"
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
        self.account_move_1 = self.account_move.create({
            "journal_id": self.account_journal_1.id,
            "partner_id": self.partner.id,
            "currency_id": self.res_cunrrency,
            "date": date(2020, 1, 1),
            'type': 'out_invoice',
            "invoice_line_ids": [(0, 0, {
                'product_id': self.product_one.id,
                'account_id': self.account_3.id,
                'quantity': 2.0,
                'price_unit': 1000,
            })]
        })
        self.account_move_1.post()
        self.asset_asset = self.account_asset.create({
            'name': "Tets asset",
            'first_depreciation_date': date(2020, 4, 30),
            'method_number': 5,
            'method_number_colgap': 10,
            'method_period': '1',
            'method_period_colgap': '1',
            'original_value': 3657000,
            'original_value_colgap': 3657000,
            'value_residual': 3657000,
            'value_residual_colgap': 3657000,
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

    def test_depreciate_asset_close(self):
        self.asset_asset.validate()
        self.sell = self.asset_sell.create({
            'action': 'dispose',
            'loss_account_id': self.account_1.id,
            'loss_account_colgap_id': self.account_1.id,
            'asset_id': self.asset_asset.id
        })
        self.sell.do_action()

    def test_depreciate_asset_close_date_validate(self):
        self.asset_asset.validate()
        self.sell = self.asset_sell.create({
            'action': 'dispose',
            'loss_account_id': self.account_1.id,
            'loss_account_colgap_id': self.account_1.id,
            'asset_id': self.asset_asset.id
        })
        for move in self.asset_asset.depreciation_move_ids:
            move.post()
        for move in self.asset_asset.depreciation_move_colgap_ids:
            move.post()
        self.sell.do_action()

    def test_depreciate_asset_close_invoice_line_id(self):
        self.asset_asset.validate()
        self.sell = self.asset_sell.create({
            'action': 'dispose',
            'loss_account_id': self.account_1.id,
            'loss_account_colgap_id': self.account_1.id,
            'asset_id': self.asset_asset.id
        })
        for move in self.asset_asset.depreciation_move_ids:
            move.post()
        for move in self.asset_asset.depreciation_move_colgap_ids:
            move.post()
        self.asset_asset._get_disposal_moves(
            [self.asset_asset.depreciation_move_colgap_ids], date(2020, 4, 30))
        self.sell.do_action()

    def test_depreciate_asset_close_invoice_line_id_else(self):
        self.asset_asset.validate()
        self.sell = self.asset_sell.create({
            'action': 'dispose',
            'loss_account_id': self.account_1.id,
            'loss_account_colgap_id': self.account_1.id,
            'asset_id': self.asset_asset.id
        })
        for move in self.asset_asset.depreciation_move_ids:
            move.post()
        for move in self.asset_asset.depreciation_move_colgap_ids:
            move.post()
        self.asset_asset._get_disposal_moves([''], date(2020, 4, 30))
        self.sell.do_action()

    def test_depreciate_asset_close_invoice_line_id_with_invoice(self):
        self.asset_asset.validate()
        self.sell = self.asset_sell.create({
            'action': 'sell',
            'loss_account_id': self.account_1.id,
            'loss_account_colgap_id': self.account_1.id,
            'asset_id': self.asset_asset.id,
            'invoice_id': self.account_move_1.id
        })
        self.sell.do_action()
        self.sell.do_action()

    # def test_depreciate_asset_close_1(self):
    #     print("OK")
    #     self.asset_asset.validate()
    #     self.sell = self.asset_sell.create({
    #         'action': 'dispose',
    #         'loss_account_id': self.account_1.id,
    #         'loss_account_colgap_id': self.account_1.id,
    #         'asset_id': self.asset_asset.id
    #     })
    #     self.sell.do_action()
    #     for move in self.asset_asset.depreciation_move_ids:
    #         move.post()
    #     for move in self.asset_asset.depreciation_move_colgap_ids:
    #         move.post()

    # def test_depreciate_asset_close_2(self):
    #     print("OK2")
    #     self.asset_asset.compute_depreciation_board()
    #     self.asset_asset.validate()
    #     self.sell = self.asset_sell.create({
    #         'action': 'dispose',
    #         'loss_account_id': self.account_1.id,
    #         'loss_account_colgap_id': self.account_1.id,
    #         'asset_id': self.asset_asset.id
    #     })
    #     self.sell.do_action()

    # def test_depreciate_asset_close_3(self):
    #     print("OK3")
    #     self.asset_asset.validate()
    #     self.sell = self.asset_sell.create({
    #         'action': 'dispose',
    #         'loss_account_id': self.account_1.id,
    #         'loss_account_colgap_id': self.account_1.id,
    #         'asset_id': self.asset_asset.id
    #     })
    #     self.sell.do_action()
