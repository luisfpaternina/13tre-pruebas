from odoo import fields
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestPurchaseOrder(TransactionCase):

    def setUp(self):
        super(TestPurchaseOrder, self).setUp()

        self.HrEmployee = self.env['hr.employee']
        self.HrJob = self.env['hr.job']

        self.ResPartner = self.env['res.partner']
        self.PurchaseOrder = self.env['purchase.order']
        # self.PurchaseOrderLine = self.env['purchase.order.line']
        self.Product = self.env['product.product']
        self.ProductCategory = self.env['product.category']
        self.MailComposeMessage = self.env['mail.compose.message']

        self.purchase = self.PurchaseOrder.create({
            'date_order': fields.Datetime.now()
        })

        self.category_one = self.ProductCategory.create({
            'name': 'All'
        })

        self.product_one = self.Product.create({
            'name': 'product one',
            'categ_id': self.category_one.id,
            'type': 'consu',
            'lst_price': 10,
            'standard_price': 8,
            'sale_ok': True,
            'purchase_ok': True
        })

        self.purchar_order_lines = [
            (0, 0, {
                'name': self.product_one.name,
                'product_id': self.product_one.id,
                'product_qty': 5,
                'price_unit': 10,
                'date_planned': fields.Datetime.now(),
                'product_uom': 1
            })
        ]

        self.purchase_with_products = self.PurchaseOrder.create({
            'date_order': fields.Datetime.now(),
            'order_line': self.purchar_order_lines
        })

        self.provider = self.ResPartner.create({
            'company_type': 'company',
            'name': 'Company Test'
        })

        self.job = self.HrJob.create({
            'name': 'Dirección comercial'
        })

        self.contact = self.ResPartner.create({
            'name': 'Pepe contact',
            'email': 'pepe@gmail.com'
        })

        self.employee = self.HrEmployee.create({
            'name': 'Pepe',
            # 'names': 'Pepe',
            # 'surnames': 'Perez',
            # 'known_as': 'Pepito',
            # 'document_type': '13',
            'identification_id': '12302356',
            'job_id': self.job.id,
            'address_id': self.contact.id
        })

    def test_add_follower_to_purchase(self):
        self.purchase.action_rfq_send()
        self.purchase.action_rfq_send()

    def test_send_message(self):
        self.purchase.message_post()
        self.purchase.with_context(mark_rfq_as_sent=True).message_post()
        self.purchase.with_context(mark_rfq_as_sent=False).message_post()

    def test_update_purchase(self):
        self.purchase.write({
            'partner_id': self.provider.id
        })

    def test_approved_oc_without_products(self):
        with self.assertRaises(ValidationError):
            self.purchase.write({
                'state': 'purchase'
            })

    def test_approver_oc_whithout_director(self):
        with self.assertRaises(ValidationError):
            self.purchase.write({
                'order_line': self.purchar_order_lines,
                'state': 'to approve'
            })

            self.purchase.button_approve()

    def test_approved_success(self):
        self.purchase_with_products.write({
            'partner_id': self.provider.id
        })

        self.purchase_with_products.action_approve_oc()
        self.purchase_with_products.button_approve()
        self.purchase_with_products.action_rfq_send()
        self.purchase_with_products\
            .get_restrict_action_move('action_approve_oc_')
