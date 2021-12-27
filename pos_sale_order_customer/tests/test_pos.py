# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.tests import common, Form
from odoo import fields

from random import randint
from datetime import datetime

from .common import (TestPointOfSaleCommon, TestPoSCommon)


class TestPos(TestPointOfSaleCommon, TestPoSCommon):

    def setUp(self):
        super(TestPos, self).setUp()
        self.config = self.basic_config
        self.PosOrder = self.env['pos.order']
        self.picking_id = self.env['stock.picking']
        self.sit = self.env['stock.immediate.transfer']

        journal_general = self.env['account.journal'].create({
            'name': 'General Journal - Test',
            'code': 'TSJ',
            'type': 'general',
            'company_id': self.company_id
        })

        self.account_move_id = self.env['account.move'].create({
            'partner_id': self.partner1.id,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product3.id,
                'quantity': 2,
                'price_unit': 100,
                'price_subtotal': 1000
            }), (0, 0, {
                'product_id': self.product4.id,
                'quantity': 2,
                'price_unit': 100,
                'price_subtotal': 1000
            })],
        })

    def test_order_to_picking_without_origin(self):
        self.pos_config.open_session_cb()
        current_session = self.pos_config.current_session_id

        self.pos_order_pos2 = self.PosOrder.create({
            'company_id': self.company_id,
            'session_id': current_session.id,
            'pricelist_id': self.partner1.property_product_pricelist.id,
            'partner_id': self.partner1.id,
            'lines': [(0, 0, {
                'name': "OL/0003",
                'product_id': self.product3.id,
                'price_unit': 450,
                'discount': 0.0,
                'qty': (-2.0),
                'tax_ids': [(6, 0, self.product3.taxes_id.ids)],
                'price_subtotal': 5000,
                'price_subtotal_incl': 5000,
            }), (0, 0, {
                'name': "OL/0004",
                'product_id': self.product4.id,
                'price_unit': 300,
                'discount': 0.0,
                'qty': (-3.0),
                'tax_ids': [(6, 0, self.product4.taxes_id.ids)],
                'price_subtotal': 1000,
                'price_subtotal_incl': 1000,
            })],
            'amount_tax': 0,
            'amount_total': 6000,
            'amount_paid': 0,
            'amount_return': 0,
        })

        context_make_payment = {
            "active_ids": [self.pos_order_pos2.id],
            "active_id": self.pos_order_pos2.id
        }

        self.pos_make_payment_3 = self.PosMakePayment\
            .with_context(context_make_payment).create({
                'amount': 6000
            })

        context_payment = {'active_id': self.pos_order_pos2.id}
        self.pos_make_payment_3.with_context(context_payment).check()

        self.assertEqual(
            self.pos_order_pos2.state,
            'paid',
            'Order should be in paid state.'
        )

        self.pos_order_pos2.create_picking()

        self.assertEqual(
            self.pos_order_pos2.picking_id.state,
            'done',
            'Picking should be in done state.'
        )

        self.assertEqual(
            self.pos_order_pos2.picking_id.move_lines.mapped('state'),
            ['done', 'done'],
            'Move Lines should be in done state.'
        )

    def test_order_to_picking_with_origin_invoice(self):
        journal_general = self.env['account.journal'].create({
            'name': 'General Journal - Test',
            'code': 'TSJ1',
            'type': 'general',
            'company_id': self.company_id
        })

        self.sale_order_id = self.env['sale.order'].create({
            'partner_id': self.partner1.id,
            'date_order': datetime.today().date(),
            'order_line': [(0, 0, {
                'product_id': self.product3.id,
                'product_uom_qty': 2,
                'price_unit': 100,
                'price_subtotal': 1000
            }), (0, 0, {
                'product_id': self.product4.id,
                'product_uom_qty': 2,
                'price_unit': 100,
                'price_subtotal': 1000
            })],
        })

        self.sale_order_id.state = "sale"
        self.sale_order_id.action_confirm()

        picking_so = self.picking_id.search([
            ('id', '=', self.sale_order_id.picking_ids[0].id)
        ])

        picking_so.state = "done"

        self.account_move_id = self.env['account.move'].create({
            'partner_id': self.partner1.id,
            'invoice_origin': self.sale_order_id.name,
            'invoice_line_ids': [(0, 0, {
                'product_id': self.product3.id,
                'quantity': 2,
                'price_unit': 100,
                'price_subtotal': 1000
            }), (0, 0, {
                'product_id': self.product4.id,
                'quantity': 2,
                'price_unit': 100,
                'price_subtotal': 1000
            })],
        })

        self.pos_config.open_session_cb()
        current_session = self.pos_config.current_session_id

        self.pos_order_pos = self.PosOrder.create({
            'company_id': self.company_id,
            'session_id': current_session.id,
            'pricelist_id': self.partner1.property_product_pricelist.id,
            'partner_id': self.partner1.id,
            'origin_invoice_pos_id': self.account_move_id.id,
            'lines': [(0, 0, {
                'name': "OL/0003",
                'product_id': self.product3.id,
                'price_unit': 450,
                'discount': 0.0,
                'qty': (-2.0),
                'tax_ids': [(6, 0, self.product3.taxes_id.ids)],
                'price_subtotal': 5000,
                'price_subtotal_incl': 5000,
            }), (0, 0, {
                'name': "OL/0004",
                'product_id': self.product4.id,
                'price_unit': 300,
                'discount': 0.0,
                'qty': (-3.0),
                'tax_ids': [(6, 0, self.product4.taxes_id.ids)],
                'price_subtotal': 1000,
                'price_subtotal_incl': 1000,
            })],
            'amount_tax': 0,
            'amount_total': 6000,
            'amount_paid': 0,
            'amount_return': 0,
        })

        context_make_payment = {
            "active_ids": [self.pos_order_pos.id],
            "active_id": self.pos_order_pos.id
        }

        self.pos_make_payment_3 = self.PosMakePayment\
            .with_context(context_make_payment).create({
                'amount': 6000
            })

        context_payment = {'active_id': self.pos_order_pos.id}
        self.pos_make_payment_3.with_context(context_payment).check()
        self.pos_order_pos.create_picking()

    def test_order_to_picking_with_origin_so(self):

        self.sale_order_id = self.env['sale.order'].create({
            'partner_id': self.partner1.id,
            'date_order': datetime.today().date(),
            'order_line': [(0, 0, {
                'product_id': self.product3.id,
                'product_uom_qty': 2,
                'price_unit': 100,
                'price_subtotal': 1000
            }), (0, 0, {
                'product_id': self.product4.id,
                'product_uom_qty': 2,
                'price_unit': 100,
                'price_subtotal': 1000
            })],
        })

        self.sale_order_id.state = "sale"
        self.sale_order_id.action_confirm()

        picking_so = self.picking_id.search([
            ('id', '=', self.sale_order_id.picking_ids[0].id)
        ])

        picking_so.state = "done"
        self.pos_config.open_session_cb()
        current_session = self.pos_config.current_session_id

        self.pos_order_pos = self.PosOrder.create({
            'company_id': self.company_id,
            'session_id': current_session.id,
            'pricelist_id': self.partner1.property_product_pricelist.id,
            'partner_id': self.partner1.id,
            'origin_sale_order_pos_id': self.sale_order_id.id,
            'lines': [(0, 0, {
                'name': "OL/0003",
                'product_id': self.product3.id,
                'price_unit': 450,
                'discount': 0.0,
                'qty': (-2.0),
                'tax_ids': [(6, 0, self.product3.taxes_id.ids)],
                'price_subtotal': 5000,
                'price_subtotal_incl': 5000,
            }), (0, 0, {
                'name': "OL/0004",
                'product_id': self.product4.id,
                'price_unit': 300,
                'discount': 0.0,
                'qty': (-3.0),
                'tax_ids': [(6, 0, self.product4.taxes_id.ids)],
                'price_subtotal': 1000,
                'price_subtotal_incl': 1000,
            })],
            'amount_tax': 0,
            'amount_total': 6000,
            'amount_paid': 0,
            'amount_return': 0,
        })

        context_make_payment = {
            "active_ids": [self.pos_order_pos.id],
            "active_id": self.pos_order_pos.id
        }

        self.pos_make_payment_3 = self.PosMakePayment\
            .with_context(context_make_payment).create({
                'amount': 6000
            })

        context_payment = {'active_id': self.pos_order_pos.id}
        self.pos_make_payment_3.with_context(context_payment).check()
        self.pos_order_pos.create_picking()

    def test_order_to_picking_with_invoice(self):
        self.pos_config.open_session_cb()
        current_session = self.pos_config.current_session_id

        self.pos_order_pos = self.PosOrder.create({
            'company_id': self.company_id,
            'session_id': current_session.id,
            'pricelist_id': self.partner1.property_product_pricelist.id,
            'partner_id': self.partner1.id,
            'origin_invoice_pos_id': self.account_move_id.id,
            'lines': [(0, 0, {
                'name': "OL/0003",
                'product_id': self.product3.id,
                'price_unit': 450,
                'discount': 0.0,
                'qty': (-2.0),
                'tax_ids': [(6, 0, self.product3.taxes_id.ids)],
                'price_subtotal': 5000,
                'price_subtotal_incl': 5000,
            }), (0, 0, {
                'name': "OL/0004",
                'product_id': self.product4.id,
                'price_unit': 300,
                'discount': 0.0,
                'qty': (-3.0),
                'tax_ids': [(6, 0, self.product4.taxes_id.ids)],
                'price_subtotal': 1000,
                'price_subtotal_incl': 1000,
            })],
            'amount_tax': 0,
            'amount_total': 6000,
            'amount_paid': 0,
            'amount_return': 0,
        })

        context_make_payment = {
            "active_ids": [self.pos_order_pos.id],
            "active_id": self.pos_order_pos.id
        }

        self.pos_make_payment_3 = self.PosMakePayment\
            .with_context(context_make_payment).create({
                'amount': 6000
            })

        context_payment = {'active_id': self.pos_order_pos.id}
        self.pos_make_payment_3.with_context(context_payment).check()
        self.pos_order_pos.create_picking()

    def test_process_order(
        self, customer=False,
        is_invoiced=False,
        payments=None, uid=None
    ):
        self.open_new_session()
        product_quantity_pairs = ([self.product3, 2], [self.product4, 2])
        data = self.create_ui_order_data(product_quantity_pairs)
        data['invoice_origin_pos'] = self.account_move_id.id
        self.PosOrder._process_order(data, True, False)

    def test_process_order_pos_order_close(
        self, customer=False,
        is_invoiced=False,
        payments=None, uid=None
    ):
        self.open_new_session()
        product_quantity_pairs = ([self.product3, 2], [self.product4, 2])
        data = self.create_ui_order_data(product_quantity_pairs)
        data['invoice_origin_pos'] = self.account_move_id.id
        pos_session = self.env['pos.session'].browse(
            data['data']['pos_session_id']
        )

        pos_session.state = 'closed'
        self.PosOrder._process_order(data, True, False)

    def test_process_order_pos_order_close(
        self, customer=False,
        is_invoiced=False,
        payments=None, uid=None
    ):
        self.open_new_session()
        product_quantity_pairs = ([self.product3, 2], [self.product4, 2])
        data = self.create_ui_order_data(product_quantity_pairs)
        data['invoice_origin_pos'] = self.account_move_id.id
        self.PosOrder._process_order(data, True, data['data'])
