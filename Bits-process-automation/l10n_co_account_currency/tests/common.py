# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from odoo.fields import Date
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestAccountCurrencyCommon(TransactionCase):

    def setUp(self):
        super(TestAccountCurrencyCommon, self).setUp()
        self.company = self.env.ref('base.main_company')
        self.company.country_id = self.env.ref('base.co')
        self.company.template_code = '01'

        self.partner = self.env['res.partner'].create({
            'name': "TST Partner",
        })

        self.account_type_sale = self.env['account.account.type'].create({
            'name': 'income',
            'type': 'other',
            'internal_group': 'income',
        })
        self.account_sale = self.env['account.account'].create({
            'name': 'Product Sales ',
            'code': 'S200000',
            'user_type_id': self.account_type_sale.id,
            'company_id': self.company.id,
            'reconcile': False
        })
        self.sale_journal = self.env['account.journal'].create({
            'name': 'reflets.info',
            'code': 'ref',
            'type': 'sale',
            'company_id': self.company.id,
            'sequence_id': self.env['ir.sequence'].search([], limit=1).id,
            'default_credit_account_id': self.account_sale.id,
            'default_debit_account_id': self.account_sale.id
        })
        self.account = self.env['account.account'].create({
            'code': "111005",
            'name': "TST Account",
            'user_type_id': (
                self.env.ref('account.data_account_type_liquidity').id),
            'reconcile': True
        })
        self.tax_group_1 = self.env['account.tax.group'].create(
            {'name': 'IVA'})
        self.tax_group_2 = self.env['account.tax.group'].create(
            {'name': 'ReteFuente'})

        self.tax = self.env['account.tax'].create({
            'name': 'Tax 19%',
            'amount': 19,
            'type_tax_use': 'sale',
            'tax_group_id': self.tax_group_1.id
        })

        self.retention_tax = self.env['account.tax'].create({
            'name': 'TEST: RteFte -3.50% Ventas',
            'amount': -3.50,
            'type_tax_use': 'sale',
            'tax_group_id': self.tax_group_2.id
        })

        self.retention_tax2 = self.env['account.tax'].create({
            'name': 'TEST: RteIVA 15% sobre el 19% IVA Ventas%',
            'amount': -15,
            'type_tax_use': 'sale',
            'tax_group_id': self.tax_group_2.id
        })
        tax_lines = [
            self.tax.id,
            self.retention_tax.id,
            self.retention_tax2.id
        ]
        self.salesperson = self.env.ref('base.user_admin')
        self.salesperson.function = 'Sales'
        self.invoice_dicc = {
            'type': 'out_invoice',
            'invoice_user_id': self.salesperson.id,
            'name': 'OC 123',
            'journal_id': self.sale_journal.id,
            'partner_id': self.partner.id,
            'currency_id': self.company.currency_id.id,
            'line_ids': [(0, 0, {
                'account_id': self.account.id,
                'product_id': self.env.ref("product.product_product_4").id,
                'partner_id': self.partner.id,
                'credit': 660000,
                'price_unit': 660000,
                "tax_ids": [(6, 0, tax_lines)]
            }), (0, 0, {
                'account_id': self.account.id,
                'partner_id': self.partner.id,
                'tax_line_id': self.tax.id,
                'price_unit': 125400,
                'credit': 125400,
                'tax_base_amount': 660000,
                'name': "TEST: IVA Ventas 19%",
            }), (0, 0, {
                'account_id': self.account.id,
                'partner_id': self.partner.id,
                'tax_line_id': self.retention_tax.id,
                'price_unit': -23100,
                'debit': 23100,
                'tax_base_amount': 660000,
                'name': 'TEST: RteFte -3.50% Ventas',
            }), (0, 0, {
                'account_id': self.account.id,
                'partner_id': self.partner.id,
                'tax_line_id': self.retention_tax2.id,
                'price_unit': -18810,
                'debit': 18810,
                'tax_base_amount': 660000,
                'name': 'RteIVA 15% sobre el 19% IVA Ventas',
            }), (0, 0, {
                'account_id': self.account.id,
                'partner_id': self.partner.id,
                'debit': 743490,
                'price_unit': -743490,
            })],
            'invoice_line_ids': [(0, 0, {
                'product_id': self.env.ref("product.product_product_4").id,
                'quantity': 1,
                'account_id': self.account_sale.id,
                'price_unit': 660000,
                'credit': 660000,
                'partner_id': self.partner.id,
                "tax_ids": [(6, 0, tax_lines)]
            })],
        }
