from datetime import datetime, date
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestPurchaseSupplierPerformance(TransactionCase):

    def setUp(self):
        super(TestPurchaseSupplierPerformance, self).setUp()
        self.purchase_order = self.env['purchase.order']
        self.res_partner = self.env['res.partner']
        self.res_company = self.env.company
        self.res_partner = self.env['res.partner']
        self.res_partner_performance = self.env['res.partner.performance']
        self.supplier_qualification = self.env['supplier.qualification.wizard']
        self.partner = self.res_partner.create({
            'name': "partner Test"
        })
        self.order = self.purchase_order.create({
            'name': "Testy order",
            'partner_id': self.partner.id
        })
        self.partner_performance = self.res_partner_performance.create({
            'partner_id': self.partner.id,
            'type': 'supplier',
            'performance': '3'
        })
        self.qualification_wizard = self.supplier_qualification.create({
            'performance': '3',
            'description': "Test Qualification"
        })

    def test_supplier_qualification(self):
        self.order.supplier_qualification()

    def test_get_default_user(self):
        self.partner_performance._get_default_user()

    def test_get_default_company(self):
        self.partner_performance._get_default_company()

    def test_create_partner_performance(self):
        self.qualification_wizard.with_context(
            order_id=self.order.id,
            partner_id=self.partner.id,
            type_qualification='supplier').create_partner_performance()

    def test_action_view_invoice(self):
        with self.assertRaises(ValidationError):
            self.order.action_view_invoice()

        self.qualification_wizard.with_context(
            order_id=self.order.id,
            partner_id=self.partner.id,
            type_qualification='supplier').create_partner_performance()
        self.order.action_view_invoice()
