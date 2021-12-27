
# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, CacheMiss, UserError
from odoo.tests import Form
from unittest.mock import patch, Mock


class TestCredit(TransactionCase):

    def setUp(self):
        super(TestCredit, self).setUp()
        self.sale_order = self.env['sale.order']
        self.partner_id = self.env['res.partner'].create({
            'name': 'Partner Test'
        })
        self.services = self.env['product.product'].search(
            [('type', '=', 'service')]
        )
        self.invoices = self.env['account.move'].search(
            [('state', '!=', 'posted')]
        )
        self.sale_order_base = self.sale_order.create({
            'name': 'Test',
            'partner_id': self.partner_id.id,
            'order_line': [
                (0, 0, {
                    'product_id': self.services[3].id,
                    'product_uom_qty': 1,
                    'price_unit': 12500,
                })
            ]
        })
        self.sale_order_base.action_confirm()
        self.res_bank_id = self.env['res.bank'].search([])[0]
        self.credit_type_id = self.env['credit.type'].create({
            'name': 'Credit Type Test',
            'code': 'ASJ23',
            'description': 'Credit type for credits',
            'supporting_entity_ids': [(6, 0, [self.res_bank_id.id, ])]
        })
        self.credit_id = self.env['credit'].create({
            'state': 'active',
            'res_partner_id': self.partner_id.id,
            'credit_type_id': self.credit_type_id.id,
            'number_credit': 1222332,
            'modality': 'revolving',
            'credit_limit': 100000000,
            'available_balance': 100000000,
            'sponsoring_entity_id': self.res_bank_id.id
        })

    def test_calculate_credit_allow_warning(self):
        self.sale_order_base.calculate_credit_allow()
        self.credit_id.update({
            'state': 'in_debt'
        })
        self.sale_order_base.calculate_credit_allow()

    def test_create_invoce_delivered(self):
        url = 'odoo.addons.sale.models.sale.SaleOrder._create_invoices'
        credit_wizard = Form(self.env[
            'sale.advance.payment.inv'].with_context({
                'default_advance_payment_method': 'delivered',
                'default_partner_id': self.partner_id.id,
                'default_sale_order_id': self.sale_order_base.id,
                'active_ids': [self.sale_order_base.id, ]
            }))
        choose_credit_option = credit_wizard.save()
        with patch(url, new=Mock(return_value=self.invoices[0])):
            choose_credit_option.create_invoices()

    def test_create_invoce(self):
        url = 'odoo.addons.sale.models.sale.SaleOrder._create_invoices'
        credit_wizard = Form(self.env[
            'sale.advance.payment.inv'].with_context({
                'default_partner_id': self.partner_id.id,
                'default_sale_order_id': self.sale_order_base.id,
                'active_ids': [self.sale_order_base.id, ]
            }))
        choose_credit_option = credit_wizard.save()
        choose_credit_option._get_partner_id_field()
        with patch(url, new=Mock(return_value=self.invoices[1])):
            choose_credit_option.create_invoices()
            inv = self.invoices[1]
            inv.action_post()

    def test_create_invoce_many_active_ids(self):
        sale_order_test = self.sale_order.create({
            'name': 'Test',
            'partner_id': self.partner_id.id,
            'order_line': [
                (0, 0, {
                    'product_id': self.services[3].id,
                    'product_uom_qty': 1,
                    'price_unit': 12500,
                })
            ]
        })
        credit_wizard = Form(self.env[
            'sale.advance.payment.inv'].with_context({
                'default_partner_id': self.partner_id.id,
                'default_sale_order_id': self.sale_order_base.id,
                'active_ids': [sale_order_test.id, self.sale_order_base.id]
            }))
        with self.assertRaises(CacheMiss):
            choose_credit_option = credit_wizard.save()
            choose_credit_option._get_partner_id_field()

    def test_create_invoce_action_post_with_error(self):
        url = 'odoo.addons.sale.models.sale.SaleOrder._create_invoices'
        credit_wizard = Form(self.env[
            'sale.advance.payment.inv'].with_context({
                'default_partner_id': self.partner_id.id,
                'default_sale_order_id': self.sale_order_base.id,
                'active_ids': [self.sale_order_base.id, ]
            }))
        choose_credit_option = credit_wizard.save()
        with patch(url, new=Mock(return_value=self.invoices[1])):
            choose_credit_option.create_invoices()
        inv = self.invoices[1]
        inv.update({
            'credit_payment': True,
            'credit': self.credit_id.id,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': self.services[3].id,
                    'quantity': 1,
                    'price_unit': 100200500,
                })
            ]
        })
        with self.assertRaises(ValidationError):
            inv.action_post()

    def test_create_invoce_action_post(self):
        url = 'odoo.addons.sale.models.sale.SaleOrder._create_invoices'
        credit_wizard = Form(self.env[
            'sale.advance.payment.inv'].with_context({
                'default_partner_id': self.partner_id.id,
                'default_sale_order_id': self.sale_order_base.id,
                'active_ids': [self.sale_order_base.id, ]
            }))
        choose_credit_option = credit_wizard.save()
        with patch(url, new=Mock(return_value=self.invoices[1])):
            choose_credit_option.create_invoices()
        inv = self.invoices[1]
        inv.update({
            'credit_payment': True,
            'credit': self.credit_id.id,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': self.services[3].id,
                    'quantity': 1,
                    'price_unit': 500,
                })
            ]
        })
        inv.action_post()

    def test_create_invoce_action_post_fixed(self):
        url = 'odoo.addons.sale.models.sale.SaleOrder._create_invoices'
        credit_wizard = Form(self.env[
            'sale.advance.payment.inv'].with_context({
                'default_advance_payment_method': 'fixed',
                'default_partner_id': self.partner_id.id,
                'default_fixed_amount': 1,
                'deafult_payment_credit': True,
                'default_credit': self.credit_id.id,
                'default_sale_order_id': self.sale_order_base.id,
                'active_ids': [self.sale_order_base.id, ]
            }))
        choose_credit_option = credit_wizard.save()
        with patch(url, new=Mock(return_value=self.invoices[1])):
            choose_credit_option.create_invoices()
        inv = self.invoices[1]
        inv.update({
            'credit_payment': True,
            'credit': self.credit_id.id,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': self.services[3].id,
                    'quantity': 1,
                    'price_unit': 11111,
                })
            ]
        })
        inv.action_post()

    def test_create_invoce_action_post_delivered(self):
        url = 'odoo.addons.sale.models.sale.SaleOrder._create_invoices'
        credit_wizard = Form(self.env[
            'sale.advance.payment.inv'].with_context({
                'default_advance_payment_method': 'delivered',
                'default_partner_id': self.partner_id.id,
                'deafult_payment_credit': True,
                'default_credit': self.credit_id.id,
                'default_sale_order_id': self.sale_order_base.id,
                'active_ids': [self.sale_order_base.id, ]
            }).create({'payment_credit': True}))
        choose_credit_option = credit_wizard.save()
        with patch(url, new=Mock(return_value=self.invoices[1])):
            choose_credit_option.create_invoices()
        inv = self.invoices[1]
        inv.update({
            'credit_payment': True,
            'credit': self.credit_id.id,
            'invoice_line_ids': [
                (0, 0, {
                    'product_id': self.services[3].id,
                    'quantity': 1,
                    'price_unit': 11111,
                })
            ]
        })
        inv.action_post()

    def test_create_invoce_no_product_create(self):
        url = 'odoo.addons.sale.models.sale.SaleOrder._create_invoices'
        credit_wizard = Form(self.env[
            'sale.advance.payment.inv'].with_context({
                'default_advance_payment_method': 'fixed',
                'default_partner_id': self.partner_id.id,
                'default_fixed_amount': 1,
                'deafult_payment_credit': True,
                'default_credit': self.credit_id.id,
                'default_sale_order_id': self.sale_order_base.id,
                'active_ids': [self.sale_order_base.id, ]
            }).create(
                {'payment_credit': True, 'product_id': self.services[3].id}
            )
        )
        choose_credit_option = credit_wizard.save()
        with self.assertRaises(UserError):
            choose_credit_option.create_invoices()
        self.services[3].update(
            {
                'invoice_policy': 'order',
            }
        )
        with patch(url, new=Mock(return_value=self.invoices[1])):
            choose_credit_option.create_invoices()

    def test_create_invoce_product_id_service(self):
        url = 'odoo.addons.sale.models.sale.SaleOrder._create_invoices'
        fiscal_position = self.env['account.fiscal.position'].create({
            'name': 'BurgerLand',
            'is_taxcloud': True,
        })
        self.sale_order_base.update({
            'fiscal_position_id': fiscal_position.id,
        })
        credit_wizard = Form(self.env[
            'sale.advance.payment.inv'].with_context({
                'open_invoices': True,
                'default_advance_payment_method': 'fixed',
                'default_partner_id': self.partner_id.id,
                'default_fixed_amount': 1,
                'deafult_payment_credit': True,
                'default_credit': self.credit_id.id,
                'default_sale_order_id': self.sale_order_base.id,
                'active_ids': [self.sale_order_base.id, ]
            }).create(
                {'payment_credit': True, 'product_id': self.services[3].id}
            )
        )
        choose_credit_option = credit_wizard.save()
        self.services[3].update(
            {
                'invoice_policy': 'order',
                'type': 'consu'
            }
        )
        with self.assertRaises(UserError):
            choose_credit_option.create_invoices()
        self.services[3].update(
            {
                'invoice_policy': 'order',
                'type': 'service'
            }
        )
        with patch(url, new=Mock(return_value=self.invoices[1])):
            choose_credit_option.create_invoices()
