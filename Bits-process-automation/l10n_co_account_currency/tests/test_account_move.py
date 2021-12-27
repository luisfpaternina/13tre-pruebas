from datetime import date, datetime, timedelta
from odoo.addons.l10n_co_account_currency.tests.common \
    import TestAccountCurrencyCommon
from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestAccountMove(TestAccountCurrencyCommon):

    def setUp(self):
        super(TestAccountMove, self).setUp()

    def test_compute_local_invoice_taxes_by_group(self):
        invoice = self.env['account.move'].new(self.invoice_dicc)
        invoice._compute_local_invoice_taxes_by_group()

    def test_compute_is_show_other_currency(self):
        invoice = self.env['account.move'].new(self.invoice_dicc)
        invoice._compute_is_show_other_currency()

    def test_compute_amount(self):
        invoice = self.env['account.move'].new(self.invoice_dicc)
        invoice._compute_amount()

    def test_compute_is_show_other_currency_in_invoice(self):
        move = self.invoice_dicc.copy()
        move['type'] = 'in_invoice'
        invoice = self.env['account.move'].new(move)
        invoice._compute_is_show_other_currency()

    def test_compute_local_invoice_taxes_by_group_in_invoice(self):
        move = self.invoice_dicc.copy()
        move['type'] = 'in_invoice'
        invoice = self.env['account.move'].new(move)
        invoice._compute_local_invoice_taxes_by_group()
