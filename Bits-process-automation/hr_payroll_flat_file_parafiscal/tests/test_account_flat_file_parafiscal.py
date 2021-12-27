import odoo.tests

from datetime import date
from datetime import datetime, timedelta

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo import fields, models, tools
from odoo.modules.module import get_module_resource


class TestAccountFlatFileParafiscal(TransactionCase):

    def setUp(self):
        super(TestAccountFlatFileParafiscal, self).setUp()

        self.AccountJournal = self.env['account.journal']
        self.AccountAccount = self.env['account.account']
        self.ResBank = self.env['res.bank']
        self.Respartner = self.env['res.partner']
        self.ResPartnerBank = self.env['res.partner.bank']
        self.AccountAnalytic = self.env['account.analytic.account']
        self.FlatFile = self.env['account.flat.file.base']
        self.ResCompany = self.env['res.company'].search([])

        self.env['ir.config_parameter'].sudo().set_param(
            'percentage_workload', float(100))

        self.env['ir.config_parameter'].sudo().set_param(
            'hr_payroll.integrate_payroll_news', True)

        test_country = self.env['res.country'].create({
            'name': "L'Île de la Mouche",
            'code': 'YY',
        })

        test_state = self.env['res.country.state'].create(dict(
            name="State",
            code="ST",
            l10n_co_divipola="0001",
            country_id=test_country.id))

        town = self.env['res.country.town'].create(dict(
            name="town",
            code="TW",
            l10n_co_divipola="0011",
            state_id=test_state.id,
            country_id=test_country.id))

        self.contact = self.Respartner.create({
            'name': 'partner name',
            'town_id': town.id
        })

        self.ir_sequence = self.env['ir.sequence'].create({
            'name': 'SEQ',
            'padding': 4,
            'number_increment': 1,
        })

        self.account_journal = self.AccountJournal.create({
            'name': 'MISC',
            'code': 'MSC',
            'type': 'general',
            'sequence_id': self.ir_sequence.id,
        })

        self.account_bank = self.AccountAccount.create({
            'code': "10151206",
            'name': "TEST Account Bank",
            'user_type_id': self.env.ref(
                'account.data_account_type_liquidity').id
        })
        self.account_payable = self.AccountAccount.create({
            'code': "23151206",
            'name': "TEST Account Payable",
            'user_type_id': self.env.ref(
                'account.data_account_type_payable').id,
            'reconcile': True
        })
        self.account_receivable = self.AccountAccount.create({
            'code': "21151206",
            'name': "TEST Account Payable",
            'user_type_id': self.env.ref(
                'account.data_account_type_receivable').id,
            'reconcile': True
        })
        self.res_partner = self.Respartner.create({
            'name': "Test Partner",
            'property_account_payable_id': self.account_payable.id,
            'property_account_receivable_id': self.account_receivable.id
        })
        self.res_bank = self.ResBank.create({
            'name': "Test Res Bank",
            'bic': "5"
        })
        self.res_partner_bank = self.ResPartnerBank.create({
            'bank_id': self.res_bank.id,
            'partner_id': self.ResCompany.partner_id.id,
            'acc_number': "159753456"
        })
        self.journal_bank = self.env['account.journal'].create({
            "name": "Test Bank",
            "code": "TESB",
            "type": "bank",
            'default_credit_account_id': self.account_bank.id,
            'default_debit_account_id':  self.account_bank.id,
            'bank_account_id': self.res_partner_bank.id
        })

        self.hr_contract = self.env['hr.contract']
        self.hr_payslip = self.env['hr.payslip']
        self.hr_employee = self.env['hr.employee']
        self.hr_salary_rule = self.env['hr.salary.rule']
        self.hr_salary_rule_category = self.env['hr.salary.rule.category']
        self.hr_payroll_structure = self.env['hr.payroll.structure']
        self.hr_payroll_structure_type = self.env['hr.payroll.structure.type']
        self.hr_payroll_news = self.env['hr.payroll.news']

        self.payable_type_id = self.env.ref(
            'account.data_account_type_payable')

        self.salary_rule_category = self.hr_salary_rule_category.create({
            'name': "Salary Category Test",
            'code': "SCT"
        })

        self.structure_type = self.hr_payroll_structure_type.create({
            'name': "Test Type",
            'wage_type': "monthly"
        })

        self.contract = self.hr_contract.create({
            'name': "Contract Test",
            'date_start': datetime.now(),
            'date_end': datetime.now()+timedelta(days=365),
            'wage': 3150000,
            'structure_type_id': self.structure_type.id
        })

        self.contract_001 = self.hr_contract.create({
            'name': "Contract 001",
            'date_start': datetime.now(),
            'date_end': datetime.now()+timedelta(days=365),
            'wage': 3150000,
            'structure_type_id': self.structure_type.id
        })

        self.account_analytic = self.AccountAnalytic.create({
            'name': 'TEST',
            'code': '0001'
        })

        self.employee = self.hr_employee.create({
            'name': "Test Payroll News",
            'contract_id': self.contract.id,
            'document_type': '13',
            'identification_id': "75395146",
            'names': 'NOMBRE1 NOMBRE2',
            'surnames': 'APELLIDO1 APELLIDO2',
            'known_as': 'SuperCode',
            'address_home_id': self.contact.id,
            'employee_center_cost_ids': [(0, 0, {
                'percentage': 100.00,
                'account_analytic_id': self.account_analytic.id
            })]
        })

        self.employee_001 = self.hr_employee.create({
            'name': "Empoyee 001",
            'contract_id': self.contract_001.id,
            'document_type': '13',
            'identification_id': "75334146",
            'names': 'NOMBRE1 NOMBRE2',
            'surnames': 'APELLIDO1 APELLIDO2',
            'known_as': 'SuperCode',
            'address_home_id': self.contact.id,
            'employee_center_cost_ids': [(0, 0, {
                'percentage': 100.00,
                'account_analytic_id': self.account_analytic.id
            })]
        })

        self.payroll_structure = self.hr_payroll_structure.create({
            'name': "Structure Test",
            'type_id': self.structure_type.id,
            'journal_id': self.account_journal.id,
        })

        self.payroll_structure_2 = self.hr_payroll_structure.create({
            'name': "Structure Test 2",
            'type_id': self.structure_type.id,
            'journal_id': self.account_journal.id,
        })

        self.salary_rule_01 = self.hr_salary_rule.create({
            'name': "TEST RULE NOVELTY",
            'code': "002",
            'sequence': 100,
            'struct_id': self.payroll_structure_2.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 30,
            "account_debit": self.account_payable.id,
            "account_credit": self.account_payable.id,
        })

        self.salary_rule = self.hr_salary_rule.create({
            'name': "ITEM PARAFISCAL",
            'code': "001",
            'sequence': 50,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1.0,
            "account_debit": self.account_payable.id,
            "account_credit": self.account_payable.id,
        })

        self.payslip = self.hr_payslip.create({
            'name': "Payroll Test",
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'journal_id': self.account_journal.id,
            'struct_id': self.payroll_structure.id,
            'general_state': 'approved',
            'date_from': datetime.now(),
            'date_to': datetime.now()+timedelta(days=365)
        })

        self.payslip_without_novelties = self.hr_payslip.create({
            'name': "Payroll Test",
            'employee_id': self.employee_001.id,
            'contract_id': self.contract_001.id,
            'journal_id': self.account_journal.id,
            'struct_id': self.payroll_structure.id,
            'general_state': 'approved',
            'date_from': datetime.now() + timedelta(days=1),
            'date_to': datetime.now()+timedelta(days=365)
        })

        self.stage_id = self.env['hr.payroll.news.stage'].search(
            [('is_approved', '=', True)])

        self.novelty = self.hr_payroll_news.create({
            'name': 'Novelty Tests',
            'payroll_structure_id': self.payroll_structure_2.id,
            'salary_rule_id': self.salary_rule_01.id,
            'date_start': datetime.now(),
            'date_end': datetime.now(),
            'request_date_from': datetime.now(),
            'request_date_to': datetime.now() + timedelta(days=5),
            'kanban_state': 'done',
            'stage_id': self.stage_id.id,
            'employee_payroll_news_ids': [(0, 0, {
                'employee_id': self.employee.id,
                'quantity': 20,
                'amount': 100
            })]
        })

        self.payroll_new = self.env['hr.payroll.news'].create({
            'name': "Test Novelty",
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule.id,
            'kanban_state': "done",
            'date_start': datetime.now(),
            'date_end': datetime.now() + timedelta(days=5),
            'request_date_from': datetime.strptime(
                '2020-12-20', '%Y-%m-%d'
            ),
            'request_date_to': datetime.strptime(
                '2020-12-22', '%Y-%m-%d'
            ),
            'stage_id': self.stage_id.id,
            'employee_payroll_news_ids': [(0, 0, {
                'employee_id': self.employee.id,
                'quantity': 1,
                'amount': 100
            })]
        })

        self.termination = self.ref(
            'hr_payroll_settlement.reason_dsjc_nor')

        self.settlement = self.env['settlement.history'].create({
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'date_payment': datetime.now(),
            'reason_for_termination': self.termination,
            'compensation': False,
        })
        self.payslip = self.hr_payslip.create({
            'name': "Payroll Test",
            'date_from': "2020-12-20",
            'date_to': "2020-12-22",
            'employee_id': self.employee.id,
            'contract_id': self.contract.id
        })

    def test_flat_file_payroll(self):
        flat_file = self.FlatFile.new({
            'template_modality': '1',
            'template_type': 'E',
            'file_extension': "txt",
            'file_type': 'get_collect_data_parafiscal'
        })
        flat_file.with_context(flat_file_payroll=True).export_flat_file()

    def test_export_flat_file_account(self):
        flat_file = self.FlatFile.new({
            'template_modality': '1',
            'template_type': 'E',
            'file_extension': "txt",
            'file_type': 'get_collect_data_parafiscal'
        })
        flat_file.export_flat_file()

    def test_flat_file_payroll_with_date(self):
        flat_file = self.FlatFile.new({
            'template_modality': '1',
            'template_type': 'E',
            'file_extension': "txt",
            'file_type': 'get_collect_data_parafiscal',
            'date_from': "2020-12-20",
            'date_to': "2020-12-22"
        })
        flat_file.with_context(flat_file_payroll=True).export_flat_file()

    def test_flat_file_payroll_csv_with_date(self):
        flat_file = self.FlatFile.new({
            'template_modality': '1',
            'template_type': 'E',
            'file_extension': "csv",
            'file_type': 'get_collect_data_parafiscal',
            'date_from': "2020-12-20",
            'date_to': "2020-12-22"
        })
        flat_file.with_context(flat_file_payroll=True).export_flat_file()

    def test_flat_file_payroll_structure(self):
        self.payslip.compute_sheet()
        flat_file = self.FlatFile.new({
            'template_modality': '1',
            'template_type': 'E',
            'file_extension': "csv",
            'file_type': 'get_collect_data_parafiscal',
            'date_from': "2020-12-20",
            'date_to': "2020-12-22",
            'struct_ids': [(6, 0, [self.payroll_structure.id])]
        })
        flat_file.with_context(flat_file_payroll=True).export_flat_file()
