from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import date


class TestAccountAgedRefReceivablePayable(TransactionCase):

    def setUp(self):
        super(TestAccountAgedRefReceivablePayable, self).setUp()
        self.aged_partner = self.env['account.aged.partner']
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
        self.partner_1 = self.res_partner.create({
            'name': "TST Partner 1"
        })
        self.account = self.account_account.create({
            'code': "111005",
            'name': "TST Account",
            'user_type_id': (
                self.env.ref('account.data_account_type_liquidity').id),
            'reconcile': True,
            'create_asset': "no"
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

    def test_get_partner_lines(self):
        options = {'date': {'date_to': date(2020, 7, 22)}}
        self.aged_partner._get_columns_name(options)

    def test_get_lines(self):
        move1 = self.account_move.create({
            'name': "/",
            'journal_id': self.journal.id,
            'date': date(2020, 7, 22),
            'type': "entry",
            'line_ids': [(0, 0, {
                'account_id': self.account.id,
                'partner_id': self.partner_1.id,
                'debit': 1000,
                'date_maturity': date(2020, 7, 22),
            }), (0, 0, {
                'account_id': self.account.id,
                'partner_id': self.partner_1.id,
                'credit': 1000,
                'date_maturity': date(2020, 7, 22),
            })]
        })
        move1.action_post()
        move2 = self.account_move.create({
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
        move2.action_post()
        self.move.action_post()
        options = {'date': {'date_to': date(
            2020, 7, 22)}, 'unfolded_lines': ['partner_{0}'.format(
                self.partner_1.id)]}
        self.aged_partner.with_context(
            date_to=date(2020, 7, 22),
            account_type='payable')._get_lines(
                options)

    def test_get_lines_with_partner(self):
        move1 = self.account_move.create({
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
        move1.action_post()
        self.move.action_post()
        options = {'date': {'date_to': date(
            2020, 7, 22)}, 'unfolded_lines': []}
        self.aged_partner.with_context(
            date_to=date(2020, 7, 22),
            account_type='payable',
            no_format=True)._get_lines(
                options, 'partner_{0}'.format(self.partner.id))

    def test_get_lines_with_partner_without_id(self):
        move1 = self.account_move.create({
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
        move1.action_post()
        self.move.action_post()
        options = {'date': {'date_to': date(
            2020, 7, 22)}, 'unfolded_lines': []}
        self.aged_partner.with_context(
            date_to=date(2020, 7, 22),
            account_type='payable')._get_lines(
                options, 'partner_')
