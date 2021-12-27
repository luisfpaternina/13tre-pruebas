# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.tests import common, Form
from odoo.exceptions import UserError


class TestDeliveryCarrier(TransactionCase):

    def setUp(self):
        super(TestDeliveryCarrier, self).setUp()
        self.delivery_carrier = self.env['delivery.carrier']
        self.free_delivery = self.env.ref('delivery.free_delivery_carrier')

        self.product = self.env['product.product'].search([], limit=1)
        self.country = self.env['res.country'].search(
            [('l10n_co_dian_code', '=', 169)])
        self.state = self.env['res.country.state'].search(
            [('l10n_co_divipola', '=', 19)])
        self.town_to = self.env['res.country.town'].search(
            [('l10n_co_divipola', '=', 19075)])

        self.delivery_carrier = self.delivery_carrier.create({
            'name': 'TEST 1',
            'product_id': self.product.id,
            'amount': 1000,
            'country_ids': [(4, self.country.id, 0)],
            'state_ids': [(4, self.state.id, 0)],
            'town_to_ids': [(4, self.town_to.id, 0)],
        })

        self.partner = self.env['res.partner'].create({
            'name': 'Test Partner',
            'country_id': self.country.id,
            'state_id': self.state.id,
            'town_id': self.town_to.id,
        })

        self.delivery_sale_order_cost = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'order_line': [(0, 0, {
                'name': 'Service on demand',
                'product_id': self.product.id,
                'product_uom_qty': 24,
                'price_unit': 75.00,
            })],
        })

    def test_town_to(self):

        delivery_wizard = Form(self.env[
            'choose.delivery.carrier'].with_context({
                'default_order_id': self.delivery_sale_order_cost.id,
                'default_carrier_id': self.free_delivery.id
            }))
        choose_delivery_carrier = delivery_wizard.save()
        choose_delivery_carrier.button_confirm()

    def test_not_town_to(self):
        town_to = self.env['res.country.town'].search(
            [('l10n_co_divipola', '=', 19001)])

        self.partner.write({
            'town_id': town_to.id
        })
        delivery_wizard = Form(self.env[
            'choose.delivery.carrier'].with_context({
                'default_order_id': self.delivery_sale_order_cost.id,
                'default_carrier_id': self.free_delivery.id
            }))
        choose_delivery_carrier = delivery_wizard.save()
        choose_delivery_carrier.button_confirm()

    def test_validate_delivery_type(self):
        self.delivery_carrier._onchange_delivery_type()
        self.assertEqual(self.delivery_carrier.price_kilogram, 0)

        self.delivery_carrier.write({
            'delivery_type': 'base_on_rule'})
        self.delivery_carrier._onchange_delivery_type()

        self.delivery_carrier.write({
            'price_kilogram': '22',
            'price_rule_ids': [
                (0, 0, {
                    'variable': 'price_kilogram',
                    'operator': '>',
                    'max_value': 22000,
                    'list_price': 1,
                    'variable_factor': 'price_kilogram',
                })
            ]
        })

        with self.assertRaises(UserError):
            self.delivery_carrier._get_price_from_picking(5000, 5, 4, 1)

        result = self.delivery_carrier._get_price_from_picking(
            5000, 3000, 4, 1)
        self.assertEqual(result, 66000)
