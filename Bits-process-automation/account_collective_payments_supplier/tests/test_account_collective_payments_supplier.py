from datetime import date, datetime
from odoo.addons.account_collective_payments_supplier.tests.common \
    import TestAccountCollectivePaymentsSupplierBase
from odoo.exceptions import UserError, ValidationError


class TestAccountCollectivePaymentsSupplier(
        TestAccountCollectivePaymentsSupplierBase):

    def setUp(self):
        super(TestAccountCollectivePaymentsSupplier, self).setUp()

    def test_onchange_supplier_payment(self):
        record = self.wizard_ref.new({
            'date_from_f': '2021-01-01',
            'date_to_f': '2021-12-31',
            'supplier_payment': True
        })
        res = record._onchange_line_list()

    def test_onchange_no_supplier_payment(self):
        record = self.wizard_ref.new({
            'date_from_f': '2021-01-01',
            'date_to_f': '2021-12-31',
            'supplier_payment': False
        })
        res = record._onchange_line_list()

    def test_generate_payments_action(self):
        lines = self.env['account.move.line'].search([
            ('journal_id.type', '=', 'purchase'),
            ('account_id.internal_type', '=', 'payable'),
            ('account_id.user_type_id', '=', self.payable_type_id.id)])

        record = self.wizard_ref.new({
            'journal_id': self.journal_purchase.id,
            'currency_id': self.currency_id.id,
            'date_from_f': '2021-01-01',
            'date_to_f': '2021-12-31',
            'line_ids': lines,
            'supplier_payment': True,
            'payment_date': datetime.now().strftime('%Y-%m-01')
        })
        record.generate_payments_action()
        self.wizard_ref.generate_payments_action()

        supplier_payment = self.collective_supplier_payment.search([])[0]
        supplier_payment._compute_currency()
        supplier_payment._compute_payments_count()
        supplier_payment.payments_view()

    def test_generate_payments_action_no_supplier_payment(self):
        lines = self.env['account.move.line'].search([
            ('journal_id.type', '=', 'purchase'),
            ('account_id.internal_type', '=', 'payable'),
            ('account_id.user_type_id', '=', self.payable_type_id.id)])

        record = self.wizard_ref.new({
            'journal_id': self.journal_purchase.id,
            'currency_id': self.currency_id.id,
            'date_from_f': '2021-01-01',
            'date_to_f': '2021-12-31',
            'line_ids': lines,
            'payment_date': datetime.now().strftime('%Y-%m-01')
        })
        record.generate_payments_action()
        self.wizard_ref.generate_payments_action()
