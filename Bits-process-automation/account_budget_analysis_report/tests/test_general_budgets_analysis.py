from odoo.tests.common import TransactionCase
from datetime import datetime, timedelta, date


class TestGeneralBudgetsAnalysis(TransactionCase):

    def setUp(self):
        super(TestGeneralBudgetsAnalysis, self).setUp()
        self.Budget = self.env['crossovered.budget']
        self.Budget_lines = self.env['crossovered.budget.lines']
        self.Company = self.env['res.company']
        self.Account_budget = self.env['account.budget.post']
        self.Account_Analytic = self.env['account.analytic.account']
        self.Account_Anccount = self.env['account.account']
        self.General_budget = self.env['general.budget.analysis']
        self.Account_Type = self.env['account.account.type']
        self.account_move = self.env['account.move']
        self.account_journal = self.env['account.journal']
        self.res_partner = self.env['res.partner']

        self.res_partner_1 = self.res_partner.create({
            'name': "TST Partner"
        })

        self.company_1 = self.Company.create({
            "name": "Bits Americas"
        })

        self.journal = self.account_journal.create({
            'name': 'Test Journal',
            'type': 'general',
            'code': 'TSTJ1',
            'company_id': self.env.company.id
        })

        self.account_analytic_1 = self.Account_Analytic.create({
            "code": 1,
            "name": "Cuenta analitica gasto"
        })

        self.account_type_1 = self.Account_Type.create({
            "name": "test",
            "internal_group": "asset",
            "type": "payable",
            "include_initial_balance": True
        })

        self.account_type_2 = self.Account_Type.create({
            "name": "test 2",
            "internal_group": "asset",
            "type": "receivable",
            "include_initial_balance": True
        })

        self.account_account_1 = self.Account_Anccount.create({
            "code": 1,
            "name": "cuenta gasto",
            "user_type_id": self.account_type_1.id,
            "reconcile": True
        })

        self.account_account_2 = self.Account_Anccount.create({
            "code": 2,
            "name": "cuenta ahorro",
            "user_type_id": self.account_type_2.id,
            "reconcile": True
        })

        self.account_analytic_2 = self.Account_Analytic.create({
            "code": 2,
            "name": "cuenta ahorro"
        })

        self.move_1 = self.account_move.create({
            'journal_id': self.journal.id,
            'date': date(2021, 5, 4),
            'type': 'entry',
            'company_id': self.company_1.id,
            'line_ids': [(0, 0, {
                'account_id': self.account_account_1.id,
                'analytic_account_id': self.account_analytic_1.id,
                'partner_id': self.res_partner_1.id,
                'journal_id': self.journal.id,
                'company_id': self.company_1.id,
                'date': date(2021, 5, 4),
                'credit': 0.0,
                'debit': 1000.0
            }), (0, 0, {
                'account_id': self.account_account_2.id,
                'analytic_account_id': self.account_analytic_1.id,
                'partner_id': self.res_partner_1.id,
                'journal_id': self.journal.id,
                'company_id': self.company_1.id,
                'date': date(2021, 5, 4),
                'credit': 1000.0,
                'debit': 0.0
            })]
        })

        self.account_budget_1 = self.Account_budget.create({
            "name": "Budget Test",
            "account_ids": [(6, 0, [self.account_account_1.id])]
        })

        self.budget_1 = self.Budget.create({
            "name": "test budget",
            "company_id": self.company_1.id,
            "date_from": date(2021, 1, 1),
            "date_to": date(2021, 11, 1)
        })

        self.general_budget_lines_1 = self.Budget_lines.create({
            "general_budget_id": self.account_budget_1.id,
            "analytic_account_id": self.account_analytic_1.id,
            "crossovered_budget_id": self.budget_1.id,
            "planned_amount": 12000,
            "company_id": self.company_1.id,
            "date_from": date(2021, 1, 1),
            "date_to": date(2021, 11, 1)
        })

        self.budget_lines_1 = self.General_budget.search([])

    def test_compute_amount(self):
        self.move_1.post()
        self.budget_lines_1._compute_amount()
