from datetime import datetime, date
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo.fields import Date


class TestPurchaseOrderTemplate(TransactionCase):

    def setUp(self):
        super(TestPurchaseOrderTemplate, self).setUp()
        self.PurchaseOrder = self.env['purchase.order']
        self.PurchaseOrderLine = self.env['purchase.order.line']
        self.Product = self.env['product.product']
        self.product_consu = self.Product.create({
            'name': 'Product A',
            'type': 'consu',
        })
        self.product_consu2 = self.Product.create({
            'name': 'Product B',
            'type': 'consu',
        })
        self.vendor = self.env['res.partner'].create({'name': 'vendor1'})
        self.uom_unit = self.env.ref('uom.product_uom_unit')
        self.company = self.env.user.company_id
        date_from = Date.from_string('%s-01-01' % (datetime.now().year + 1))
        date_to = Date.from_string('%s-12-31' % (datetime.now().year + 1))
        uom_id = self.env.ref('uom.product_uom_unit')
        self.purchase_order = self.PurchaseOrder.create({
            'partner_id': self.vendor.id,
            'company_id': self.company.id,
            'currency_id': self.company.currency_id.id,
            'date_order': date_from,
            'order_line': [
                (0, 0, {
                    'name': self.product_consu.name,
                    'product_id': self.product_consu.id,
                    'product_qty': 20,
                    'product_uom': uom_id.id,
                    'price_unit': 200,
                    'date_planned': date_from,
                })]
        })

    def test_action_rfq_send(self):
        self.purchase_order.action_rfq_send()

    def test_action_rfq_send_context(self):
        self.purchase_order.with_context({
            'send_rfq': False
        }).action_rfq_send()
