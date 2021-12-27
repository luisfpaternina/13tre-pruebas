# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.tests import common, Form


class TestSaleListPriceValidation(TransactionCase):

    def setUp(self):
        super(TestSaleListPriceValidation, self).setUp()
        self.product_tmpl_id = self.env['product.template']
        self.product_prod_id = self.env['product.product']
        self.category_id = self.env['product.category']
        self.product_pricelist_id = self.env['product.pricelist']

        self.category_id = self.category_id.create({
            'name': 'Test Category'
        })

        self.product_tmpl_id = self.product_tmpl_id.create({
            'name': 'Test Product Template',
            'default_code': 'Product Test 001',
            'categ_id': self.category_id.id,
            'standard_price': 1.99,
            'list_price': 2.10,
        })

        self.product_prod_id = self.product_prod_id.create({
            'name': 'Test Product Product',
            'default_code': 'Variant Test 001',
            'categ_id': self.category_id.id,
            'standard_price': 1.99,
            'list_price': 2.10,
        })

    def test_applied_on_is_product_tmpl(self):
        self.product_pricelist_id = self.product_pricelist_id.create({
            'name': 'Test Product List Price',
            'item_ids': [(
                0, 0, {
                    'applied_on': '1_product',
                    'product_tmpl_id': self.product_tmpl_id.id,
                    'compute_price': 'fixed',
                    'fixed_price': 1.01
                }
            )]
        })

    def test_applied_on_is_prod_prod(self):
        self.product_pricelist_id = self.product_pricelist_id.create({
            'name': 'Test Product List Price',
            'item_ids': [(
                0, 0, {
                    'applied_on': '0_product_variant',
                    'product_id': self.product_prod_id.id,
                    'compute_price': 'fixed',
                    'fixed_price': 1.01
                }
            )]
        })

    def test_applied_on_is_all_prod(self):
        self.product_pricelist_id = self.product_pricelist_id.create({
            'name': 'Test Product List Price',
            'item_ids': [(
                0, 0, {
                    'applied_on': '3_global',
                    'compute_price': 'fixed',
                    'fixed_price': 1.01
                }
            )]
        })

    def test_price_list_is_higher(self):
        self.product_pricelist_id = self.product_pricelist_id.create({
            'name': 'Test Product List Price',
            'item_ids': [(
                0, 0, {
                    'applied_on': '1_product',
                    'product_tmpl_id': self.product_tmpl_id.id,
                    'compute_price': 'fixed',
                    'fixed_price': 3.01
                }
            )]
        })

    def test_compute_price_is_not_fixed(self):
        self.product_pricelist = self.product_pricelist_id.create({
            'name': 'Test Product List Price',
            'item_ids': [(
                0, 0, {
                    'applied_on': '3_global',
                    'compute_price': 'percentage',
                    'percent_price': 2
                }
            )]
        })
        self.product_pricelist.item_ids.list_price_validation()
