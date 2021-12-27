from datetime import datetime, date
from dateutil.relativedelta import relativedelta

from odoo.fields import Date
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo.tests import Form


class TestPurcharseBudget(TransactionCase):

    def setUp(self):
        super(TestPurcharseBudget, self).setUp()
        self.PurchaseOrder = self.env['purchase.order']
        self.PurchaseOrderLine = self.env['purchase.order.line']
        self.BudgetPost = self.env['account.budget.post']
        self.company = self.env.user.company_id

        account_id = self.env['account.account'].create({
            'name': 'Product Sales - (test)',
            'code': 'X2020',
            'user_type_id': self.ref('account.data_account_type_revenue'),
            'tag_ids': [(6, 0, [self.ref('account.account_tag_operating')])],
        })

        self.Product = self.env['product.product']
        self.product_consu = self.Product.create({
            'name': 'Product A',
            'type': 'consu',
            'property_account_expense_id': account_id.id,
        })

        self.product_consu2 = self.Product.create({
            'name': 'Product B',
            'type': 'consu',
        })
        self.vendor = self.env['res.partner'].create({'name': 'vendor1'})
        self.uom_unit = self.env.ref('uom.product_uom_unit')
        date_from = Date.from_string('%s-01-01' % (datetime.now().year + 1))
        date_to = Date.from_string('%s-12-31' % (datetime.now().year + 1))

        self.account_budget_post_sales0 = self.BudgetPost.create({
            'name': 'Sales',
            'account_ids': [(6, None, account_id.ids)],
        })

        # Creating a crossovered.budget record
        self.budget = self.env['crossovered.budget'].create({
            'date_from': date_from,
            'date_to': date_to,
            'name': 'Budget %s' % (datetime.now().year + 1),
            'state': 'draft'
        })

        self.budget_line_1 = self.env['crossovered.budget.lines'].create({
            'crossovered_budget_id': self.budget.id,
            'general_budget_id': self.account_budget_post_sales0.id,
            'analytic_account_id': self.ref(
                'analytic.analytic_partners_camp_to_camp'),
            'date_from': date_from,
            'date_to': date_to,
            'planned_amount': 10000.0,
        })
        self.budget_line_2 = self.env['crossovered.budget.lines'].create({
            'crossovered_budget_id': self.budget.id,
            'analytic_account_id': self.ref(
                'analytic.analytic_our_super_product'),
            'date_from': Date.from_string(
                '%s-09-01' % (datetime.now().year + 1)),
            'date_to': Date.from_string(
                '%s-09-30' % (datetime.now().year + 1)),
            'planned_amount': 400000.0,
        })

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
                    'account_analytic_id': self.ref(
                        'analytic.analytic_partners_camp_to_camp'),
                    'price_unit': 200,
                    'date_planned': date_from,
                })]
        })

    def test_is_excess_budget(self):
        self.purchase_order.order_line._is_excess_budget()

    def test_compute_notify_email_to(self):
        self.purchase_order._compute_notify_email_to()

    def test_purchase_order_confirm(self):
        self.purchase_order.button_confirm()
        self.assertEqual(
            self.purchase_order.budget_approval_state, 'approved')

    def test_purchase_order_confirm_excess(self):
        self.purchase_order.order_line.write({'product_qty': 20000})
        self.purchase_order.button_confirm()
        self.assertEqual(
            self.purchase_order.budget_approval_state, 'excess')

    def test_purchase_order_line_confirm(self):
        po = Form(self.PurchaseOrder)
        po.partner_id = self.vendor
        with po.order_line.new() as po_line:
            po_line.product_id = self.product_consu
            po_line.product_qty = 1
            po_line.price_unit = 100
        with po.order_line.new() as po_line:
            po_line.product_id = self.product_consu2
            po_line.product_qty = 10
            po_line.price_unit = 200
        po = po.save()
        po.button_confirm()
        self.assertEqual(po.budget_approval_state, 'excess')

    def test_purchase_order_approve(self):
        vals = {
            'partner_id': self.vendor.id,
            'company_id': self.company.id,
            'currency_id': self.company.currency_id.id,
            'date_order': '2019-01-01',
        }
        purchase_order = self.PurchaseOrder.with_context(
            tracking_disable=True).new(vals.copy())
        purchase_order.button_approve()
        self.assertEqual(purchase_order.budget_approval_state, 'approved')

    def test_purchase_order_approve_excess(self):
        self.purchase_order.order_line.write({'product_qty': 20000})
        self.purchase_order.button_approve()
        self.assertEqual(self.purchase_order.budget_approval_state, 'excess')

    def test_purchase_order_action_notification_send(self):
        self.purchase_order.action_notification_send()
        self.purchase_order.with_context(
            {'send_budget_approval': True}).action_notification_send()

    def test_purchase_order_message_post(self):
        self.purchase_order.message_post()
        self.purchase_order.with_context(
            {'mark_up_budget_sent': True}).message_post()
