# -*- coding: utf-8 -*-

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase
from datetime import datetime


class TestStockIncome(TransactionCase):

    def setUp(self):
        super(TestStockIncome, self).setUp()
        self.res_partner = self.env['res.partner']
        self.category_product = self.env['product.category']
        self.tmpl_product = self.env['product.template']
        self.product = self.env['product.product']
        self.sequence = self.env['ir.sequence']
        self.stock_type = self.env['stock.picking.type']
        self.stock_move = self.env['stock.move']
        self.stock_location = self.env['stock.location']
        self.uom_category = self.env['uom.category']
        self.uom = self.env['uom.uom']
        self.stock = self.env['stock.picking']
        self.wizard_email_stock = self.env['send.confirmation.to.suppliers']
        self.company = self.res_partner.create({
            'company_type': 'company',
            'name': 'Azure Interior',
            'email': 'azure.interior@azure.com',
        })
        self.company2 = self.res_partner.create({
            'company_type': 'company',
            'name': 'Bits Americas',
            'email': 'ar@bits.com',
        })
        self.uom_category_test = self.uom_category.create({
            'name': 'Category test'
        })
        self.all_category = self.category_product.create({
            'name': 'All'
        })
        self.uom_test = self.uom.create({
            'name': 'Uom test',
            'category_id': self.uom_category_test.id,
            'factor': 1,
            'rounding': 1,
            'uom_type': 'reference'
        })
        self.uom_test2 = self.uom.create({
            'name': 'Uom test 2',
            'category_id': self.uom_category_test.id,
            'factor': 1,
            'rounding': 1,
            'uom_type': 'bigger'
        })
        self.product_template = self.tmpl_product.create({
            'name': 'template category',
            'sequence': 1,
            'type': 'consu',
            'categ_id': self.all_category.id,
            'uom_id': self.uom_test.id,
            'uom_po_id': self.uom_test.id
        })
        self.computer_product = self.product.create({
            'name': 'Computer ACER',
            'sale_ok': True,
            'purchase_ok': True,
            'type': 'consu',
            'categ_id': self.all_category.id,
            'uom_id': self.uom_test.id,
            'product_tmpl_id': self.product_template.id,
        })
        self.sequence_reception = self.sequence.create({
            'name': 'Sequence test',
            'implementation': 'standard',
            'active': True,
            'padding': 5,
            'number_increment': 1,
            'number_next_actual': 13,
        })
        self.reception_type = self.stock_type.create({
            'name': 'Reception',
            'sequence_id': self.sequence_reception.id,
            'sequence_code': 'IN',
            'code': 'incoming'
        })
        self.location_id = self.stock_location.create({
            'name': 'Location tests',
            'usage': 'production'
        })
        self.location_dest_id = self.stock_location.create({
            'name': 'Location tests Dest',
            'usage': 'inventory'
        })
        self.warehouse_entry = self.stock.create({
            'name': 'Warehouse Test',
            'partner_id': self.company.id,
            'picking_type_id': self.reception_type.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'scheduled_date': datetime.strftime(
                datetime.now(), '%Y-%m-%d'
            ),
            'immediate_transfer': True,
        })
        self.warehouse_entry2 = self.stock.create({
            'name': 'Warehouse Test',
            'partner_id': self.company2.id,
            'picking_type_id': self.reception_type.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'scheduled_date': datetime.strftime(
                datetime.now(), '%Y-%m-%d'
            ),
            'immediate_transfer': True,
        })
        self.move_receipt_1 = self.stock_move.create({
            'name': 'Warehouse Test',
            'product_id': self.computer_product.id,
            'quantity_done': 2,
            'product_uom': self.uom_test.id,
            'picking_id': self.warehouse_entry.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
        })
        self.move_receipt_2 = self.stock_move.create({
            'name': 'Warehouse Test',
            'product_id': self.computer_product.id,
            'quantity_done': 2,
            'product_uom': self.uom_test.id,
            'picking_id': self.warehouse_entry2.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
        })
        self.send_email = self.wizard_email_stock.with_context(
            active_ids=[self.warehouse_entry.id]
        ).create(
            {
                'is_email': False,
                'is_print': True,
                'printed': False,
                'template_id': self.env.ref(
                    'stock_income.send_confirmation_suppliers_email_template'
                ).id,
                'stock_picking_ids': [(6, 0, [self.warehouse_entry.id])]
            }
        )

    def test_wizard_lift_validation(self):
        self.warehouse_entry.button_validate()
        self.warehouse_entry.with_context(
            active_ids=[self.warehouse_entry.id]
        ).send_confirmation_of_receipt()
        self.assertEqual(self.warehouse_entry.state, 'done')

    def test_print(self):
        self.warehouse_entry.button_validate()
        self.send_email.send_and_print_action()

    def test_send_and_print(self):
        self.warehouse_entry.button_validate()
        self.send_email.with_context(
            active_ids=[self.warehouse_entry.id],
            recipient='admin@dmin.com'
        ).update({
            'is_email': True,
            'partner_ids': [(6, 0, [self.company2.id, self.company.id])]
        })
        self.send_email.onchange_is_email()
        self.send_email.send_and_print_action()

    def test_compute_composition_mode(self):
        self.warehouse_entry.button_validate()
        self.send_email.with_context(
            active_ids=[self.warehouse_entry.id, self.warehouse_entry2.id]
        ).update({
            'stock_picking_ids': [
                (6, 0, [
                    self.warehouse_entry.id,
                    self.warehouse_entry2.id,
                ])
            ]
        })
        self.send_email._compute_composition_mode()

    def test_onchange_template_id(self):
        self.warehouse_entry.button_validate()
        self.send_email.update({
            'template_id': False,
        })
        self.send_email.onchange_template_id()

    def test_onchange_template_without_composer(self):
        self.warehouse_entry.button_validate()
        self.send_email.update({
            'composer_id': False,
        })
        self.send_email.onchange_template_id()

    def test_onchange_email(self):
        self.warehouse_entry.button_validate()
        self.send_email.onchange_is_email()
        self.send_email.update({
            'is_email': True
        })
        self.send_email.onchange_is_email()

    def test_send_email(self):
        self.warehouse_entry.button_validate()
        self.send_email.with_context(
            active_ids=[self.warehouse_entry.id]
        ).update({
            'is_email': True,
            'is_print': False,
            'partner_ids': [(6, 0, [self.company2.id, self.company.id])]
        })
        self.send_email.send_and_print_action()

    def test_send_confirmation_without_done(self):
        self.send_email.with_context(
            active_ids=[self.warehouse_entry.id]
        ).update({
            'is_email': True,
            'partner_ids': [(6, 0, [self.company2.id, self.company.id])]
        })
        with self.assertRaises(UserError):
            self.send_email.send_and_print_action()

    def test_template_without_lang(self):
        self.env.ref(
            'stock_income.send_confirmation_suppliers_email_template'
        ).lang = ''
        self.warehouse_entry.button_validate()
        self.warehouse_entry.with_context(
            active_ids=[self.warehouse_entry.id]
        ).send_confirmation_of_receipt()

    def test_onchange_email_without_composer(self):
        self.warehouse_entry.button_validate()
        self.send_email._compute_composition_mode()
        self.send_email.with_context(
            active_ids=[self.warehouse_entry.id, self.warehouse_entry2]
        ).update({
            'is_email': True,
            'partner_ids': [(self.company.id)],
            'stock_picking_ids': [
                (6, 0, [
                    self.warehouse_entry.id,
                    self.warehouse_entry2.id,
                ])
            ]
        })
        self.send_email.update({
            'composer_id': False,
        })
        with self.assertRaises(Exception):
            self.send_email.onchange_is_email()
