from datetime import datetime, timedelta
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError


class TestPurchaseAccount(TransactionCase):

    def setUp(self):
        super(TestPurchaseAccount, self).setUp()
        self.AccountMove = self.env['account.move']
        self.account_id = self.env['account.account'].create({
            'name': "Test Account",
            'code': "12345687",
            'user_type_id': self.env.ref(
                'account.data_account_type_expenses').id
        })

        self.journal_id = self.env['account.journal'].create({
            "name": "Test",
            "code": "TEST",
            "type": "general"
        })

        self.partner = self.env['res.partner'].create({
            'name': "Test Name"
        })

        vals = {
            'type': 'entry',
            'partner_id': self.partner.id,
            'journal_id': self.journal_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': 'Insurance claim',
                'account_id': self.account_id.id,
                'price_unit': 450,
                'quantity': 1,
            })]
        }

        self.account_move = self.AccountMove.with_context(
            asset_type='purchase').create(vals)

    def test_action_general_state_approve(self):
        self.account_move.action_general_state_approve()

    def test_action_invoice_register_payment(self):
        with self.assertRaises(UserError):
            self.account_move.action_invoice_register_payment()
        self.account_move.action_general_state_approve()
        self.account_move.action_invoice_register_payment()

    def test_get_restrict_action_move(self):
        self.account_move.get_restrict_action_move('not_method')
