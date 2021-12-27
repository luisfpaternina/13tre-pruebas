# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.tests import common, Form
from odoo.exceptions import UserError
from unittest.mock import patch, Mock


class TestQuotation(TransactionCase):

    def setUp(self):
        super(TestQuotation, self).setUp()
        self.sale_order_id = self.env['sale.order']
        self.product_id = self.env['product.product']
        self.product_category_id = self.env['product.category']
        self.partner_id = self.env['res.partner']
        self.company = self.env['res.company'].create({'name': 'Test Company'})
        self.advisor_user = self.env['res.users'].search(
            [
                ('company_ids', 'in', (self.company.id,)),
                (
                    'groups_id',
                    'in',
                    self.env.ref('account.group_account_manager').ids
                )
            ]
        )

        self.partner_id = self.partner_id.create({
            'name': 'Partner Test',
            'email': 'test@test.com',
        })

        self.product_category_id = self.product_category_id.create({
            'name': 'Category Test',
            'apply_discount_table': True
        })

        self.product_id = self.product_id.create({
            'name': 'Product Test',
            'categ_id': self.product_category_id.id,
            'standard_price': 100,
            'list_price': 110
        })

        self.product_id_2 = self.product_id.create({
            'name': 'Product Test 2',
            'categ_id': self.product_category_id.id,
            'standard_price': 10,
            'list_price': 10
        })

    def test_calculate_sale_value_discount(self):
        product_01 = self.env.ref('product.product_product_6')
        sale_order_id_01 = self.sale_order_id.create({
            'partner_id': self.partner_id.id,
            'order_line': [(0, None, {
                'product_id': product_01.id,
                'product_uom_qty': 5,
                'discount': 1
            })]
        })
        sale_order_id_01.order_line._calculate_sale_value_discount()
        sale_order_id_01.order_line._compute_amount()
        sale_order_id_01.order_line._calculate_valid_in_category()
        sale_order_id_01._calculate_sale_discount()

    def test_calculate_valid_in_category(self):
        prod_category_id = self.product_category_id.create({
            'name': 'Category Test',
            'apply_discount_table': True
        })

        prod_id = self.product_id.create({
            'name': 'Product Test 2',
            'categ_id': prod_category_id.id,
            'standard_price': 100,
            'list_price': 110
        })

        prod_id_2 = self.product_id.create({
            'name': 'Product Test 2',
            'categ_id': prod_category_id.id,
            'standard_price': 100,
            'list_price': 0
        })

        sale_order_id_02 = self.sale_order_id.create({
            'partner_id': self.partner_id.id,
            'order_line': [(0, None, {
                'product_id': prod_id.id,
                'product_uom_qty': 5,
                'discount': 1
            })]
        })
        sale_order_id_03 = self.sale_order_id.create({
            'partner_id': self.partner_id.id,
            'order_line': [(0, None, {
                'product_id': prod_id.id,
                'product_uom_qty': 0,
                'discount': 0
            })]
        })
        url = (
            'odoo.addons.base.models.res_users.Users.has_group'
        )
        sale_order_id_02.order_line._calculate_sale_value_discount()
        with patch(url, new=Mock(return_value=False)):
            sale_order_id_02.order_line.with_context(
                {'import_file': True}
            )._compute_amount()
        sale_order_id_02.order_line._compute_amount()
        sale_order_id_02.order_line._calculate_valid_in_category()
        sale_order_id_02._calculate_sale_discount()

    def test_calculate_sale_discount(self):
        prod_category_id = self.product_category_id.create({
            'name': 'Category Test',
            'apply_discount_table': True
        })

        prod_id = self.product_id.create({
            'name': 'Product Test 2',
            'categ_id': prod_category_id.id,
            'standard_price': 100,
            'list_price': 110
        })

        sale_order_id_02 = self.sale_order_id.create({
            'partner_id': self.partner_id.id,
            'discount_order': 2,
            'order_line': [(0, None, {
                'product_id': prod_id.id,
                'product_uom_qty': 5,
                'discount': 0.00
            })]
        })
        sale_order_id_02.order_line._calculate_sale_value_discount()
        sale_order_id_02.order_line._compute_amount()
        sale_order_id_02.order_line._calculate_valid_in_category()
        sale_order_id_02._calculate_sale_discount()

    def test_subtotal_none(self):
        prod_category_id = self.product_category_id.create({
            'name': 'Category Test',
            'apply_discount_table': True
        })

        prod_id_2 = self.product_id.create({
            'name': 'Product Test 2',
            'categ_id': prod_category_id.id,
            'standard_price': 100,
            'list_price': 0
        })

        sale_order_id_03 = self.sale_order_id.create({
            'partner_id': self.partner_id.id,
            'order_line': [(0, None, {
                'product_id': prod_id_2.id,
                'product_uom_qty': 0,
                'discount': 0.00,
            })]
        })
        sale_order_id_03.order_line._calculate_sale_value_discount()
        sale_order_id_03.order_line._compute_amount()
        sale_order_id_03.order_line._calculate_valid_in_category()
        sale_order_id_03._calculate_sale_discount()

    def test_subtotal_none_2(self):
        sale_order_id_03 = self.sale_order_id.create({
            'partner_id': self.partner_id.id,
            'order_line': [(0, None, {
                'product_id': self.product_id_2.id,
                'product_uom_qty': 1,
                'discount': 0,
            })]
        })
        print("\n\n\n\n\n")
        print(sale_order_id_03.order_line.price_subtotal)
        print("\n\n\n\n\n")
        sale_order_id_03.order_line._calculate_sale_value_discount()
        sale_order_id_03.order_line._compute_amount()
