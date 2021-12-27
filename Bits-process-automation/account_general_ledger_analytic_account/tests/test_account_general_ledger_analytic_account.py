from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import date


class TestAccountGeneralLedgerAnalyticAccount(TransactionCase):

    def setUp(self):
        super(TestAccountGeneralLedgerAnalyticAccount, self).setUp()
        self.general_ledger = self.env['account.general.ledger']
        self.account_journal = self.env['account.journal']
        self.res_partner = self.env['res.partner']
        self.account_account = self.env['account.account']
        self.account_move = self.env['account.move']

        self.journal = self.account_journal.create({
            'name': "TST Journal",
            'type': "general",
            'code': "TST1"
        })
        self.partner = self.res_partner.create({
            'name': "TST Partner"
        })
        self.account = self.account_account.create({
            'code': "111005",
            'name': "TST Account",
            'user_type_id': (
                self.env.ref('account.data_account_type_liquidity').id),
            'reconcile': True
        })
        self.move = self.account_move.create({
            'name': "/",
            'journal_id': self.journal.id,
            'date': date(2020, 7, 22),
            'type': "entry",
            'line_ids': [(0, 0, {
                'account_id': self.account.id,
                'partner_id': self.partner.id,
                'debit': 1000,
                'date_maturity': date(2020, 7, 22),
            }), (0, 0, {
                'account_id': self.account.id,
                'partner_id': self.partner.id,
                'credit': 1000,
                'date_maturity': date(2020, 7, 22),
            })]
        })

    def test_get_columns_name(self):
        self.general_ledger._get_columns_name({})

    def test_get_account_title_line(self):
        self.general_ledger._get_initial_balance_line(
            {}, self.account, 0.0, 0.0, 0.0, 0.0)

    def test_get_account_total_line(self):
        self.general_ledger._get_account_total_line(
            {}, self.account, 0.0, 0.0, 0.0, 0.0)

    def test_get_total_line(self):
        self.general_ledger._get_total_line({}, 0.0, 0.0, 0.0)

    def test_get_aml_line(self):
        self.move.post()
        line = self.move.line_ids[0]
        aml = {
            'payment_id': line.payment_id.id,
            'account_id': line.account_id.id,
            'move_type': "entry",
            'ref': line.ref,
            'name': line.name,
            'currency_id': line.currency_id.id,
            'id': line.ids,
            'move_name': line.move_id.name,
            'date': line.move_id.date,
            'analytic_name': "",
            'partner_name': line.partner_id.name,
            'debit': line.debit,
            'credit': line.credit
        }
        self.general_ledger._get_aml_line({}, self.account, aml, 1000)
