# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.tests import common, Form
from odoo.exceptions import UserError


class TestQuotationApproval(TransactionCase):

    def setUp(self):
        super(TestQuotationApproval, self).setUp()
        self.sale_order_id = self.env['sale.order']
        # so_line_id = self.env['sale.order.line']
        self.product_id = self.env['product.product']
        self.product_category_id = self.env['product.category']
        self.partner_id = self.env['res.partner']
        self.table_discount_id = self.env['discount.table']
        self.res_config_settings = self.env['res.config.settings']
        self.user = self.env.ref('base.user_admin')
        self.company = self.env['res.company'].create({'name': 'Test Company'})
        self.user.write(
            {
                'company_ids': [
                    (4, self.company.id)
                ], 'company_id': self.company.id
            }
        )
        Settings = self.env['res.config.settings'].with_user(self.user.id)
        self.config = Settings.create({'min_gross_margin': 0.1})
        self.res_group = self.env.ref(
            'sale_order_discount_product.group_manager_discount_approval'
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
            'list_price': 150
        })

        self.table_discount_id = self.table_discount_id.create({
            'name': 'Table Discount Test',
            'min_quantity': 1,
            'max_quantity': 10,
            'min_discount': 0,
            'max_discount': 1
        })

    def test_validation_for_discount(self):
        sale_order_id_01 = self.sale_order_id.create({
            'partner_id': self.partner_id.id,
            'order_line': [(0, None, {
                'product_id': self.product_id.id,
                'product_uom_qty': 5,
                'discount': 1
            })]
        })
        sale_order_id_01.order_line._calculate_sale_value_discount()
        sale_order_id_01.order_line._compute_amount()
        sale_order_id_01.order_line._calculate_valid_in_category()
        sale_order_id_01._calculate_sale_discount()
        sale_order_id_01.validation_for_discount()
        sale_order_id_01.update({
            'order_line': [
                (
                    0, None, {
                        'product_id': self.product_id.id,
                        'product_uom_qty': 5,
                        'discount': 1,
                        'price_unit': 1,
                    }
                )
            ]
        })
        sale_order_id_01.validation_for_discount()
        sale_order_id_01.send_for_approval()

    # vfd = Valid for discount
    def test_vfd_without_valid_category(self):
        self.product_id.categ_id.update({'apply_discount_table': False})
        sale_order_id_01 = self.sale_order_id.create({
            'partner_id': self.partner_id.id,
            'order_line': [(0, None, {
                'product_id': self.product_id.id,
                'product_uom_qty': 5,
                'discount': 1
            })]
        })
        sale_order_id_01.order_line._calculate_sale_value_discount()
        sale_order_id_01.order_line._compute_amount()
        sale_order_id_01.order_line._calculate_valid_in_category()
        sale_order_id_01._calculate_sale_discount()
        sale_order_id_01.validation_for_discount()
        sale_order_id_01.send_for_approval()

    # vfd = Valid for discount
    def test_vfd_without_valid_quantity(self):
        self.product_id.categ_id.update({'apply_discount_table': True})
        sale_order_id_01 = self.sale_order_id.create({
            'partner_id': self.partner_id.id,
            'order_line': [(0, None, {
                'product_id': self.product_id.id,
                'product_uom_qty': 100,
                'discount': 1
            })]
        })
        sale_order_id_01.order_line._calculate_sale_value_discount()
        sale_order_id_01.order_line._compute_amount()
        sale_order_id_01.order_line._calculate_valid_in_category()
        sale_order_id_01._calculate_sale_discount()
        sale_order_id_01.validation_for_discount()
        sale_order_id_01.send_for_approval()

    # vfd = Valid for discount
    def test_vfd_without_discount(self):
        self.product_id.categ_id.update({'apply_discount_table': True})
        sale_order_id_01 = self.sale_order_id.create({
            'partner_id': self.partner_id.id,
            'order_line': [(0, None, {
                'product_id': self.product_id.id,
                'product_uom_qty': 1,
                'discount': 0
            })]
        })
        sale_order_id_01.validation_for_discount()
        sale_order_id_01 = self.sale_order_id.create({
            'partner_id': self.partner_id.id,
            'order_line': [(0, None, {
                'product_id': self.product_id.id,
                'product_uom_qty': 1,
                'discount': 1
            })]
        })
        sale_order_id_01.validation_for_discount()
        sale_order_id_01.validate_discount_line_without_order_discount()

    def test_vfd_without_mb_minimum(self):
        self.product_id.categ_id.update({'apply_discount_table': True})
        self.config.create({'min_gross_margin': 0.0})
        sale_order_id_01 = self.sale_order_id.create({
            'partner_id': self.partner_id.id,
            'order_line': [(0, None, {
                'product_id': self.product_id.id,
                'product_uom_qty': 100,
                'discount': 1
            })]
        })
        sale_order_id_01.order_line._calculate_sale_value_discount()
        sale_order_id_01.order_line._compute_amount()
        sale_order_id_01.order_line._calculate_valid_in_category()
        sale_order_id_01._calculate_sale_discount()
        sale_order_id_01.validation_for_discount()
        sale_order_id_01.send_for_approval()

    def test_action_cancel_discount(self):
        sale_order_id_01 = self.sale_order_id.create({
            'partner_id': self.partner_id.id,
            'order_line': [
                (
                    0, None, {
                        'product_id': self.product_id.id,
                        'product_uom_qty': 100,
                        'discount': 1
                    }
                )
            ]
        })
        sale_order_id_01.send_for_approval()
        sale_order_id_01.action_cancel()
        sale_order_id_01.send_for_approval()
        sale_order_id_01.with_context(
            {
                'rejected_by_a_superior': True,
                'reject_discount': True
            }
        ).action_cancel()
        sale_order_id_01.send_for_approval()
        sale_order_id_01.with_context(
            {
                'rejected_by_a_superior': True,
                'reject_freight': False
            }
        ).action_cancel()
        sale_order_id_01.send_for_approval()
        sale_order_id_01.with_context(
            {
                'rejected_by_a_superior': True
            }
        ).action_cancel()

    def test_action_cancel_without_rejected_by_a_superior(self):
        sale_order_id_01 = self.sale_order_id.create({
            'partner_id': self.partner_id.id,
            'approver_discount_id': self.env.user.id,
            'approver_freight_id': self.env.user.id,
            'order_line': [
                (
                    0, None, {
                        'product_id': self.product_id.id,
                        'product_uom_qty': 100,
                        'discount': 1
                    }
                )
            ]
        })
        sale_order_id_01.send_for_approval()
        sale_order_id_01.action_cancel()

    def test_action_confirm_flow(self):
        sale_order_id_01 = self.sale_order_id.create({
            'partner_id': self.partner_id.id,
            'send_approval_discount': True,
            'send_approval_freight': True,
            'order_line': [
                (
                    0, None, {
                        'product_id': self.product_id.id,
                        'product_uom_qty': 100,
                        'discount': 1
                    }
                )
            ]
        })
        sale_order_id_01.send_for_approval()
        sale_order_id_01.action_confirm_flow()
        sale_order_id_01.send_for_approval()
        sale_order_id_01.with_context(
            {
                'approve_by_a_superior': True,
                'approve_discount': True,
            }
        ).action_confirm_flow()
        sale_order_id_01.send_for_approval()
        sale_order_id_01.with_context(
            {
                'approve_by_a_superior': True,
                'approve_freight': True,
            }
        ).action_confirm_flow()
        sale_order_id_01.update({
            'send_approval_discount': True,
            'send_approval_freight': False,
            'approver_discount_id': self.env.user.id
        })
        sale_order_id_01.send_for_approval()
        sale_order_id_01.with_context(
            {
                'approve_by_a_superior': True
            }
        ).action_confirm_flow()
        sale_order_id_01.update({
            'send_approval_discount': True,
            'send_approval_freight': False,
            'approver_discount_id': False
        })
        sale_order_id_01.send_for_approval()
        sale_order_id_01.with_context(
            {
                'approve_by_a_superior': True
            }
        ).action_confirm_flow()
        sale_order_id_01.update({
            'send_approval_discount': False,
            'send_approval_freight': True,
        })
        sale_order_id_01.send_for_approval()
        sale_order_id_01.with_context(
            {
                'approve_by_a_superior': True
            }
        ).action_confirm_flow()
        sale_order_id_01.update({
            'send_approval_discount': False,
            'send_approval_freight': True,
            'approver_freight_id': False
        })
        sale_order_id_01.send_for_approval()
        sale_order_id_01.with_context(
            {
                'approve_by_a_superior': True
            }
        ).action_confirm_flow()
        sale_order_id_01.update({
            'send_approval_discount': False,
            'send_approval_freight': False,
        })
        sale_order_id_01.send_for_approval()
        sale_order_id_01.with_context(
            {
                'approve_by_a_superior': True
            }
        ).action_confirm_flow()
