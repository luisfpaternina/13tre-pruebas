from datetime import date
from datetime import datetime, timedelta
from odoo.addons.account_collective_payments.tests.common \
    import TestAccountCollectivePaymentsBase
from odoo.exceptions import UserError, ValidationError
import logging


class TestAccountCollectivePayments(TestAccountCollectivePaymentsBase):

    def setUp(self):
        super(TestAccountCollectivePayments, self).setUp()

    def test_generate_payments_action_reconciled(self):
        lines = self.env['account.move.line'].search([
            ('account_id.user_type_id', '=', self.payable_type_id.id)])
        record = self.wizard_ref.new({
            'journal_id': self.journal_bank.id,
            'date_from_f': '2020-05-01',
            'date_to_f': '2020-05-06',
            'payment_date': '2021-09-30',
            'line_ids': lines
        })
        res = record.generate_payments_action()
        """domain = res.get('domain', False)

        if domain and domain[0][-1]:
            payment = self.env['account.payment'].browse(domain[0][-1])
            self.assertEqual(payment.state, 'posted')"""

    def test_generate_payments_check_f(self):
        self.AccountMoveLine = self.env['account.move.line']
        self.account_journal = self.env['account.journal']
        self.res_company = self.env['res.company']
        self.account_move = self.env['account.move']
        self.res_partner = self.env['res.partner']
        self.account_account = self.env['account.account']
        self.account_move = self.env['account.move']
        self.account_type = self.env['account.account.type']
        self.account_type1 = self.account_type.search([])
        self.partner = self.res_partner.create({
            'name': "TST Partner"
        })
        self.company = self.res_company.create({
            'name': "Test Company"
        })
        self.journal = self.account_journal.create({
            'name': 'Nomina',
            'type': 'general',
            'code': 'TSTJ1',
            'company_id': self.company.id
        })
        self.account = self.account_account.create({
            'code': "111005",
            'name': "TST Account",
            'user_type_id': (
                self.env.ref('account.data_account_type_liquidity').id),
            'company_id': self.company.id
        })
        self.move = self.account_move.create({
            'name': "/",
            'journal_id': self.journal.id,
            'date': date(2020, 7, 22),
            'type': "entry",
            'company_id': self.company.id,
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
        record = self.wizard_ref.new({
            'journal_id': self.journal.id,
            'date_from_f': '2020-05-01',
            'date_to_f': '2020-05-06',
            'payment_date': '2021-09-30',
            'line_ids': self.move.line_ids,
            'journal_id_f': self.journal.id,
        })
        res = record.generate_payments_check_f()

    def test_check_journal_name(self):
        self.AccountMoveLine = self.env['account.move.line']
        self.account_journal = self.env['account.journal']
        self.res_company = self.env['res.company']
        self.account_move = self.env['account.move']
        self.res_partner = self.env['res.partner']
        self.account_account = self.env['account.account']
        self.account_move = self.env['account.move']
        self.account_type = self.env['account.account.type']
        self.account_type1 = self.account_type.search([])
        self.partner = self.res_partner.create({
            'name': "TST Partner"
        })
        self.company = self.res_company.create({
            'name': "Test Company"
        })
        self.journal = self.account_journal.create({
            'name': 'Nomina',
            'type': 'general',
            'code': 'TSTJ1',
            'company_id': self.company.id
        })
        self.account = self.account_account.create({
            'code': "111005",
            'name': "TST Account",
            'user_type_id': (
                self.env.ref('account.data_account_type_liquidity').id),
            'company_id': self.company.id
        })
        self.move = self.account_move.create({
            'name': "/",
            'journal_id': self.journal.id,
            'date': date(2020, 7, 22),
            'type': "entry",
            'company_id': self.company.id,
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
        record = self.wizard_ref.new({
            'journal_id': self.journal.id,
            'date_from_f': '2020-05-01',
            'date_to_f': '2020-05-06',
            'line_ids': self.move.line_ids,
            'payment_date': '2021-09-30',
            'journal_id_f': self.journal.id,
        })
        res = record.check_journal_name()

    def test_check_payments_and_journal(self):
        self.AccountMoveLine = self.env['account.move.line']
        self.account_journal = self.env['account.journal']
        self.res_company = self.env['res.company']
        self.account_move = self.env['account.move']
        self.res_partner = self.env['res.partner']
        self.account_account = self.env['account.account']
        self.account_move = self.env['account.move']
        self.account_type = self.env['account.account.type']
        self.account_type1 = self.account_type.search([])
        self.partner = self.res_partner.create({
            'name': "TST Partner"
        })
        self.company = self.res_company.create({
            'name': "Test Company"
        })
        self.journal = self.account_journal.create({
            'name': 'Nomina',
            'type': 'general',
            'code': 'TSTJ1',
            'company_id': self.company.id
        })
        self.account = self.account_account.create({
            'code': "111005",
            'name': "TST Account",
            'user_type_id': (
                self.env.ref('account.data_account_type_liquidity').id),
            'company_id': self.company.id
        })
        self.move = self.account_move.create({
            'name': "/",
            'journal_id': self.journal.id,
            'date': date(2020, 7, 22),
            'type': "entry",
            'company_id': self.company.id,
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
        record = self.wizard_ref.new({
            'journal_id': self.journal.id,
            'date_from_f': '2020-05-01',
            'date_to_f': '2020-05-06',
            'line_ids': self.move.line_ids,
            'payment_date': '2021-09-30',
            'journal_id_f': self.journal.id,
        })
        ans = record.check_journal_name()
        answer = record.generate_payments_check_f()
        result = record.check_payments_and_journal()

    def test_generate_payments_action_t(self):
        self.AccountMoveLine = self.env['account.move.line']
        self.account_journal = self.env['account.journal']
        self.res_company = self.env['res.company']
        self.account_move = self.env['account.move']
        self.res_partner = self.env['res.partner']
        self.account_account = self.env['account.account']
        self.account_move = self.env['account.move']
        self.account_type = self.env['account.account.type']
        self.hr_payslip = self.env['hr.payslip']
        self.hr_employee = self.env['hr.employee']
        self.hr_salary_rule = self.env['hr.salary.rule']
        self.hr_salary_rule_category = self.env['hr.salary.rule.category']
        self.hr_payroll_structure = self.env['hr.payroll.structure']
        self.hr_payroll_structure_type = self.env['hr.payroll.structure.type']
        self.hr_contract = self.env['hr.contract']
        self.partner = self.res_partner.create({
            'name': "TST Partner"
        })
        self.company = self.res_company.create({
            'name': "Test Company"
        })
        self.journal = self.account_journal.create({
            'name': 'Nomina',
            'type': 'general',
            'code': 'TSTJ1',
            'company_id': self.company.id
        })
        self.salary_rule_category = self.hr_salary_rule_category.create({
            'name': "Salary Category Test",
            'code': "SCT"
        })
        self.contract = self.hr_contract.create({
            'name': "Contract Test",
            'date_start': datetime.now(),
            'date_end': datetime.now()+timedelta(days=365),
            'wage': 3150000
        })
        self.employee = self.hr_employee.create({
            'name': "Test Payroll News",
            'contract_id': self.contract.id,
            'document_type': '13',
            'identification_id': "75395146",
            'names': 'NOMBRE1 NOMBRE2',
            'surnames': 'APELLIDO1 APELLIDO2',
            'known_as': 'SuperCode',
        })
        self.structure_type = self.hr_payroll_structure_type.create({
            'name': "Test Type",
            'wage_type': "monthly"
        })
        self.payroll_structure = self.hr_payroll_structure.create({
            'name': "Structure Test",
            'type_id': self.structure_type.id,
            'journal_id': self.journal.id,
        })
        self.account = self.account_account.create({
            'code': "111005",
            'name': "TST Account",
            'user_type_id': (
                self.env.ref('account.data_account_type_liquidity').id),
            'company_id': self.company.id
        })
        self.move = self.account_move.create({
            'name': "/",
            'journal_id': self.journal.id,
            'date': date(2020, 7, 22),
            'type': "entry",
            'company_id': self.company.id,
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
        self.payslip = self.hr_payslip.create({
            'name': "Payroll Test",
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'journal_id': self.journal.id,
            'struct_id': self.payroll_structure.id,
            # 'general_state': 'approved',
            'date_from': datetime.now(),
            'date_to': datetime.now()+timedelta(days=365),
            'move_id': self.move.id
        })
        self.account_type1 = self.account_type.search([])
        record = self.wizard_ref.new({
            'journal_id': self.journal.id,
            'date_from_f': '2020-05-01',
            'date_to_f': '2020-05-06',
            'payment_date': '2021-09-30',
            'line_ids': self.move.line_ids,
            'journal_id_f': self.journal.id,
        })
        ans = record.check_journal_name()
        answer = record.generate_payments_check_f()
        result = record.check_payments_and_journal()
        record.generate_payments_action_t()

    def test_generate_payments_action_t_2(self):
        self.AccountMoveLine = self.env['account.move.line']
        self.account_journal = self.env['account.journal']
        self.res_company = self.env['res.company']
        self.account_move = self.env['account.move']
        self.res_partner = self.env['res.partner']
        self.account_account = self.env['account.account']
        self.account_move = self.env['account.move']
        self.account_type = self.env['account.account.type']
        self.hr_payslip = self.env['hr.payslip']
        self.hr_employee = self.env['hr.employee']
        self.hr_salary_rule = self.env['hr.salary.rule']
        self.hr_salary_rule_category = self.env['hr.salary.rule.category']
        self.hr_payroll_structure = self.env['hr.payroll.structure']
        self.hr_payroll_structure_type = self.env['hr.payroll.structure.type']
        self.hr_contract = self.env['hr.contract']
        self.partner = self.res_partner.create({
            'name': "TST Partner"
        })
        self.company = self.res_company.create({
            'name': "Test Company"
        })
        self.journal = self.account_journal.create({
            'name': 'Test',
            'type': 'general',
            'code': 'TSTJ1',
            'company_id': self.company.id
        })
        self.salary_rule_category = self.hr_salary_rule_category.create({
            'name': "Salary Category Test",
            'code': "SCT"
        })
        self.contract = self.hr_contract.create({
            'name': "Contract Test",
            'date_start': datetime.now(),
            'date_end': datetime.now()+timedelta(days=365),
            'wage': 3150000
        })
        self.employee = self.hr_employee.create({
            'name': "Test Payroll News",
            'contract_id': self.contract.id,
            'document_type': '13',
            'identification_id': "75395146",
            'names': 'NOMBRE1 NOMBRE2',
            'surnames': 'APELLIDO1 APELLIDO2',
            'known_as': 'SuperCode',
        })
        self.structure_type = self.hr_payroll_structure_type.create({
            'name': "Test Type",
            'wage_type': "monthly"
        })
        self.payroll_structure = self.hr_payroll_structure.create({
            'name': "Structure Test",
            'type_id': self.structure_type.id,
            'journal_id': self.journal.id,
        })
        self.account = self.account_account.create({
            'code': "111005",
            'name': "TST Account",
            'user_type_id': (
                self.env.ref('account.data_account_type_liquidity').id),
            'company_id': self.company.id
        })
        self.move = self.account_move.create({
            'name': "/",
            'journal_id': self.journal.id,
            'date': date(2020, 7, 22),
            'type': "entry",
            'company_id': self.company.id,
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
        self.payslip = self.hr_payslip.create({
            'name': "Payroll Test",
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'journal_id': self.journal.id,
            'struct_id': self.payroll_structure.id,
            # 'general_state': 'approved',
            'date_from': datetime.now(),
            'date_to': datetime.now()+timedelta(days=365),
            'move_id': self.move.id
        })
        self.account_type1 = self.account_type.search([])
        record = self.wizard_ref.new({
            'journal_id': self.journal.id,
            'date_from_f': '2020-05-01',
            'date_to_f': '2020-05-06',
            'payment_date': '2021-09-30',
            'line_ids': self.move.line_ids,
            'journal_id_f': self.journal.id,
        })
        ans = record.check_journal_name()
        answer = record.generate_payments_check_f()
        result = record.check_payments_and_journal()
        record.generate_payments_action_t()
