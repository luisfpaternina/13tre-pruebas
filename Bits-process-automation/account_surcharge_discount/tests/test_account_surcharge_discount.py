# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.tests import Form


class TestAccountSurchargeDiscount(TransactionCase):

    def setUp(self):
        super(TestAccountSurchargeDiscount, self).setUp()
        self.partner = self.env['res.partner'].create({
            'name': "TST Partner",
        })
        self.company = self.env.ref('base.main_company')
        self.company.country_id = self.env.ref('base.co')
        self.company.template_code = '01'
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
        self.salesperson = self.env.ref('base.user_admin')
        self.salesperson.function = 'Sales'
        self.invoice_dicc = {
            'type': 'out_invoice',
            'invoice_user_id': self.salesperson.id,
            'name': 'OC 123',
            'journal_id': self.sale_journal.id,
            'partner_id': self.partner.id,
            'currency_id': self.company.currency_id.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.env.ref("product.product_product_4").id,
                'quantity': 1,
                'account_id': self.account_sale.id,
                'price_unit': 660000,
                'credit': 660000,
                'partner_id': self.partner.id,
            }), (0, 0, {
                'product_id': self.env.ref("product.product_product_4").id,
                'quantity': 1,
                'account_id': self.account_sale.id,
                'price_unit': 660000,
                'credit': 660000,
                'partner_id': self.partner.id,
            })],
        }

    def test_account_surcharge_discount(self):
        _dicc = self.invoice_dicc.copy()
        invoice = self.env['account.move'].new(_dicc)
        invoice._compute_amount()
        invoice._onchange_invoice_line_ids()
        invoice.onchange_discount_type_rate()
        invoice.supply_rate()
        invoice._get_surchange_discount_data()

    def test_supply_rate(self):
        _dicc = self.invoice_dicc.copy()
        _dicc['apply_global_discount'] = True
        invoice = self.env['account.move'].new(_dicc)
        res = invoice.supply_rate()
        _dicc2 = self.invoice_dicc.copy()
        _dicc2['apply_global_discount'] = True
        _dicc2['discount_type'] = 'percent'
        _dicc2['discount_rate'] = 120
        invoice2 = self.env['account.move'].new(_dicc2)
        res = invoice2.supply_rate()
        invoice2._onchange_invoice_line_ids()
        invoice2.discount_rate = 10
        invoice2.apply_global_discount = True
        invoice2.discount_type = 'percent'
        res = invoice2.supply_rate()
        invoice2.discount_rate = 10
        invoice2.apply_global_discount = True
        invoice2.discount_type = 'amount'
        res = invoice2.supply_rate()

    def test_onchange_invoice_line_ids(self):
        _dicc = self.invoice_dicc.copy()
        invoice = self.env['account.move'].new(_dicc)
        invoice.invoice_line_ids[0].apply_discount = True
        invoice.invoice_line_ids[0].quantity = 0
        invoice._onchange_invoice_line_ids()

    def test_onchange_surchange_discount_by_line(self):
        _dicc = self.invoice_dicc.copy()
        invoice = self.env['account.move'].new(_dicc)
        for line in invoice.invoice_line_ids:
            line.apply_discount = True
            line.discount_amount = 60000
            line._get_surchange_discount_by_line()
        invoice.supply_rate()
        invoice._onchange_invoice_line_ids()
        res = invoice._get_surchange_discount_data()
        for line in invoice.invoice_line_ids:
            line.quantity = 0
            line._get_surchange_discount_by_line()
        res = invoice._get_surchange_discount_data()
