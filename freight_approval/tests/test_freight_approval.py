# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.tests import common, Form
from odoo.exceptions import UserError


class TestFreightApproval(TransactionCase):

    def setUp(self):
        super(TestFreightApproval, self).setUp()
        self.sale_order = self.env['sale.order']
        self.partner1 = self.env['res.partner'].create({
            'name': 'Partner Test'
        })
        self.product = self.env['product.product'].search([])[0]
        self.order = self.sale_order.create({
            'partner_id': self.partner1.id,
            'order_line': [
                (
                    0, 0, {
                        'product_id': self.product.id,
                        'product_uom_qty': 1,
                    }
                )
            ]
        })
        self.shipping = self.order.action_open_delivery_wizard()
        self.wizard_shipping = Form(
            self.env[self.shipping.get('res_model')].with_context(
                self.shipping.get('context')
            )
        )
        self.wizard_shipping = self.wizard_shipping.save()
        self.wizard_shipping.button_confirm()

    def test_onchange_order_line_without_cost_modified(self):
        self.order.onchange_order_line()

    def test_onchange_order_line_with_cost_modified(self):
        delivery_line = self.order.order_line.filtered('is_delivery')
        for line in delivery_line:
            if line.product_id.lst_price == line.price_unit:
                line.update({'price_unit': 4})
        self.order.onchange_order_line()

    def test_cancellation_flow(self):
        self.order.send_for_approval()
        self.order.with_context(
            {'rejected_by_a_superior': True}
        ).action_cancel()

    def test_confitmation_flow(self):
        self.order.send_for_approval()
        self.order.with_context(
            {'approve_by_a_superior': True}
        ).action_confirm()

    def test_approval_flow_normal(self):
        self.order.action_confirm()
        self.order.action_cancel()
