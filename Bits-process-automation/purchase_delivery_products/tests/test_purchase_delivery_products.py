# -*- coding: utf-8 -*-
"""Test for delivery products"""
from odoo.tests.common import TransactionCase
from datetime import datetime


class TestPurchaseDeliveryProducts(TransactionCase):
    def setUp(self):
        super(TestPurchaseDeliveryProducts, self).setUp()
        self.purchase_order = self.env['purchase.order']
        self.res_partner = self.env['res.partner']
        self.product_product = self.env['product.product']

        self.product_template = self.env['product.template']
        self.product_category = self.env['product.category']
        self.uom_uom = self.env['uom.uom']
        self.uom_category = self.env['uom.category']

        self.partner_create = self.res_partner.create({
            'name': 'Azure Test'
        })
        self.product_category_create = self.product_category.create({
            'name': 'Category Name'
        })
        self.uom_category_create = self.uom_category.create({
            'name': 'Test Category Uom'
        })
        self.uom_create = self.uom_uom.create({
            'uom_type': 'reference',
            'rounding': 0.01,
            'factor': 1.0,
            'category_id': self.uom_category_create.id,
            'name': 'Test Uom',
        })

        self.stock_location = self.env['stock.location']
        self.stock_location_create = self.stock_location.create({
            'name': 'Test Location',
            'usage': 'internal',
        })

        self.product_template_create = self.product_template.create({
            'name': 'Test product template',
            'type': 'consu',
            'categ_id': self.product_category_create.id,
            'uom_id': self.uom_create.id,
            'uom_po_id': self.uom_create.id,
            'purchase_line_warn': 'no-message',
            'tracking': 'none',
        })
        self.product_product_create = self.product_product.create({
            'product_tmpl_id': self.product_template_create.id
        })

        """Dependencies purchase order """
        self.stock_warehouse = self.env.ref('stock.warehouse0').id
        self.stock_picking_type = self.env["stock.picking.type"]

        self.stock_picking_type_create = self.stock_picking_type.create({
            'name': 'Test Picking',
            'sequence_code': 'abc',
            'code': 'incoming',
            'company_id': self.env.company.id,
            'warehouse_id': self.stock_warehouse,
            'default_location_src_id': self.stock_location_create.id,
            'default_location_dest_id': self.stock_location_create.id,
        })

        """Create purchase order """

        self.purchase_order_create = self.purchase_order.create({
            'name': 'Test Purchase',
            'date_order': datetime.now(),
            'partner_id': self.partner_create.id,
            'currency_id': self.env.company.currency_id.id,
            'company_id': self.env.company.id,
            'picking_type_id': self.stock_picking_type_create.id,
            'order_line': [(0, 0, {
                'name': 'Test Product',
                'product_qty': 2,
                'price_unit': 10.0,
                'product_id': self.product_product_create.id,
                'product_uom': self.uom_create.id,
                'date_planned': datetime.now(),

            })],
        })

    def test_compute_delivery_products(self):
        self.stock_immediate_transfer = self.env['stock.immediate.transfer']
        self.purchase_order_create.button_confirm()
        picking_ids = self.purchase_order_create.picking_ids
        self.stock_immediate_transfer.create({
            'pick_ids': [(6, 0, picking_ids.ids)],
        }).process()
        self.purchase_order_create._compute_delivered_products()
        self.purchase_order_create.action_view_invoice()
        self.assertTrue(self.purchase_order_create.delivered_products)

    def test_false_compute_delivery_products(self):
        self.purchase_order_create.button_confirm()
        self.purchase_order_create.get_restrict_action_purchase('test')
        self.purchase_order_create._compute_delivered_products()
        self.assertFalse(self.purchase_order_create.delivered_products)
