from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta, date


class TesHrPayrollAccount(TransactionCase):

    def setUp(self):
        super(TesHrPayrollAccount, self).setUp()
        self.hr_employee = self.env['hr.employee']
        self.hr_payroll_structure = self.env['hr.payroll.structure']
        self.hr_employee_payroll_news = self.env['hr.employee.payroll.news']
        self.hr_salary_rule = self.env['hr.salary.rule']
        self.hr_payroll_news_stage = self.env['hr.payroll.news.stage']
        self.hr_payroll_new = self.env['hr.payroll.news']
        self.hr_payroll_structure_type = self.env['hr.payroll.structure.type']
        self.HrPayrollStructure = self.env['hr.payroll.structure']
        self.hr_salary_rule = self.env['hr.salary.rule']
        self.hr_salary_rule_category = self.env['hr.salary.rule.category']
        self.HrSalaryRule = self.env['hr.salary.rule']
        self.hr_contract = self.env['hr.contract']
        self.hr_payslip = self.env['hr.payslip']
        self.config_settings = self.env['res.config.settings']
        self.AccountJournal = self.env['account.journal']
        self.AccountAccount = self.env['account.account']
        self.AccountAccountType = self.env['account.account.type']
        self.HrResPartner = self.env['res.partner']
        self.EmployeeCenterCost = self.env['hr.employee.center.cost']
        self.CenterCost = self.env['account.analytic.account']
        self.HrSalaryRuleCategory = self.env['hr.salary.rule.category']
        self.HrWorkEntryType = self.env['hr.work.entry.type']
        self.HrPayslipWorkedDays = self.env['hr.payslip.worked_days']

        self.env['ir.config_parameter'].sudo().set_param(
            'percentage_workload', 100)
        self.env['ir.config_parameter'].sudo().set_param(
            'hr_payroll.integrate_payroll_news', True)

        self.center_cost1 = self.CenterCost.create({
            'name': 'Desarrollo',
            'code': 'dev'
        })
        self.center_cost2 = self.CenterCost.create({
            'name': 'Administracion',
            'code': 'admin'
        })
        self.contact = self.HrResPartner.create({
            'name': 'partner name'
        })
        self.account_account_type = self.AccountAccountType.create({
            'name': 'Gastos de administración',
            'type': 'other',
            'internal_group': 'expense'
        })

        self.account_account_type_benefit = self.AccountAccountType.create({
            'name': 'Beneficios a empleados',
            'type': 'other',
            'internal_group': 'liability'
        })

        self.account_account_wage = self.AccountAccount.create({
            'code': '2505010199',
            'name': 'SUELDOS',
            'user_type_id': self.account_account_type_benefit.id
        })
        # diario contable de nomina
        self.account_journal = self.AccountJournal.create({
            'name': 'account journal test',
            'code': 'NOM',
            'type': 'general',
            'default_credit_account_id': self.account_account_wage.id
        })

        self.employee = self.hr_employee.create({
            'name': "Juan Perez",
            'names': "Juan Perez",
            'surnames': "Perez",
            'known_as': "Juan Perez",
            'document_type': '13',
            'identification_id': "98945615",
        })
        self.employee_1 = self.hr_employee.create({
            'name': "Mario Perez",
            'names': "Mario Perez",
            'surnames': "Perez",
            'known_as': "Mario Perez",
            'document_type': '13',
            'identification_id': "78945612",
            'address_home_id': self.contact.id,
            'employee_center_cost_ids': [(0, 0, {
                    'percentage': 100,
                    'account_analytic_id': self.center_cost1.id
            })]
        })

        self.payroll_structure_type = self.hr_payroll_structure_type.create({
            'name': 'Structure type test',
            'wage_type': 'monthly'
        })

        self.payroll_structure_type_01 = (
            self.hr_payroll_structure_type.create({
                'name': 'Structure type test 01',
                'wage_type': 'monthly'
            }))

        self.payroll_structure = self.HrPayrollStructure.create({
            'name': 'Structures Test',
            'type_id': self.payroll_structure_type.id,
            'journal_id': self.account_journal.id
        })
        self.payroll_structure_01 = self.HrPayrollStructure.create({
            'name': 'Structures Test 01',
            'type_id': self.payroll_structure_type_01.id,
            'journal_id': self.account_journal.id
        })
        self.base_salary_rule_category = self.HrSalaryRuleCategory.create({
            'name': 'BASIC',
            'code': 'BASIC'
        })
        self.base_salary_rule_category_01 = self.HrSalaryRuleCategory.create({
            'name': 'Deducciones',
            'code': 'DED'
        })
        self.account_salary_dev = self.AccountAccount.create({
            'code': '615530050601',
            'name': 'SALARIO BÁSICO',
            'user_type_id': self.account_account_type.id
        })
        self.account_net_salary = self.AccountAccount.create({
            'code': '25050101',
            'name': 'NOMINA POR PAGAR',
            'user_type_id': self.account_account_type.id
        })
        self.account_others_disscount = self.AccountAccount.create({
            'code': '13659503',
            'name': 'OTROS DESCUENTOS',
            'user_type_id': self.account_account_type.id
        })
        self.account_aporte_salud = self.AccountAccount.create({
            'code': '23700506',
            'name': 'APORTE SALUD',
            'user_type_id': self.account_account_type.id
        })
        self.account_aporte_pension = self.AccountAccount.create({
            'code': '23803001',
            'name': 'APORTE PENSION',
            'user_type_id': self.account_account_type.id
        })
        self.account_fondo_solidario = self.AccountAccount.create({
            'code': '23803005',
            'name': 'APORTE FONDO SOLIDATIO',
            'user_type_id': self.account_account_type.id
        })
        self.base_salary_rule_account_lines = [
            (0, 0, {
                'account_account_id': self.account_salary_dev.id,
                'account_analytic_id': self.center_cost1.id,
                'account_type': 'debit'
            })
        ]

        self.base_salary_rule = self.HrSalaryRule.create({
            'name': 'Salario Base',
            'code': 'BASIC',
            'appears_on_payslip': True,
            'sequence': 1,
            'struct_id': self.payroll_structure.id,
            'category_id': self.base_salary_rule_category.id,
            'condition_select': 'none',
            'amount_select': 'percentage',
            'quantity':
            ('worked_days.WORK100 and worked_days.WORK100.number_of_days'),
            'amount_percentage': 100.0000,
            'amount_percentage_base': 'contract.wage/30',
            'condition_range': 'contract.wage',
            'note': 'sueldo / 30 x dias trabajados',
            'non_constitutive_percentage': 100.0000,
            'constitutive_percentage': 100.0000,
            'affect_payslip': True,
            'salary_rule_account_ids': self.base_salary_rule_account_lines
        })
        # Salary rule ARL
        self.arl_salary_rule_account_lines = [
            (0, 0, {
                'account_account_id': self.account_net_salary.id,
                'account_type': 'credit'
            }),
            (0, 0, {
                'account_account_id': self.account_others_disscount.id,
                'account_type': 'debit'
            })
        ]

        self.arl_salary_rule = self.HrSalaryRule.create({
            'name': 'ARL',
            'code': 'ARL',
            'sequence': 300,
            'struct_id': self.payroll_structure.id,
            'category_id': self.base_salary_rule_category.id,
            'condition_select': 'none',
            'amount_select': 'percentage',
            'amount_percentage_base': "1",
            'quantity': "1",
            'amount_percentage': 0.5220,
            'salary_rule_account_ids': self.arl_salary_rule_account_lines
        })
        # aporte a salud inicio
        self.aporte_salud_account_lines = [
            (0, 0, {
                'account_account_id': self.account_aporte_salud.id,
                'account_type': 'credit'
            })
        ]

        self.aporte_salud_rule = self.HrSalaryRule.create({
            'name': 'APORTE SALUD',
            'code': '3010',
            'sequence': 180,
            'struct_id': self.payroll_structure.id,
            'category_id': self.base_salary_rule_category.id,
            'condition_select': 'none',
            'amount_select': 'percentage',
            'amount_percentage_base': 'payslip.paid_amount',
            'amount_percentage': -4.0000,
            'salary_rule_account_ids': self.aporte_salud_account_lines
        })

        # pension start
        self.aporte_pension_lines = [
            (0, 0, {
                'account_account_id': self.account_aporte_pension.id,
                'account_type': 'credit',

            })
        ]

        self.aporte_pension_rule = self.HrSalaryRule.create({
            'name': 'APORTE PENSION',
            'code': '3020',
            'sequence': 180,
            'struct_id': self.payroll_structure.id,
            'category_id': self.base_salary_rule_category.id,
            'condition_select': 'none',
            'amount_select': 'percentage',
            'amount_percentage_base': 'payslip.paid_amount',
            'amount_percentage': -4.0000,
            'salary_rule_account_ids': self.aporte_pension_lines
        })
        # aporte pension end

        # aporte fondo solidario start
        self.aporte_fondo_solidario_lines = [
            (0, 0, {
                'account_account_id': self.account_fondo_solidario.id,
                'account_type': 'credit'
            })
        ]

        self.aporte_fondo_solidario_rule = self.HrSalaryRule.create({
            'name': 'APORTE FONDO SOLIDARIO',
            'code': '3023',
            'sequence': 170,
            'struct_id': self.payroll_structure.id,
            'category_id': self.base_salary_rule_category.id,
            'condition_select': 'none',
            'amount_select': 'percentage',
            'amount_percentage_base': 'payslip.paid_amount',
            'amount_percentage': -1.0000,
            'salary_rule_account_ids': self.aporte_fondo_solidario_lines
        })

        # otros descuentos
        self.others_discounts_lines = [
            (0, 0, {
                'account_account_id': self.account_others_disscount.id,
                'account_type': 'credit'
            })
        ]

        self.others_discounts = self.HrSalaryRule.create({
            'name': 'Otros descuentos',
            'code': '3305',
            'sequence': 129,
            'struct_id': self.payroll_structure_01.id,
            'category_id': self.base_salary_rule_category_01.id,
            'condition_select': 'none',
            'amount_select': 'fix',
            'quantity': '1',
            'amount_fix': -200000,
            'salary_rule_account_ids': self.others_discounts_lines
        })

        # net salary start
        self.net_salary_rule_account_lines = [
            (0, 0, {
                'account_account_id': self.account_net_salary.id,
                'account_type': 'credit'
            })
        ]

        self.net_salary_rule = self.HrSalaryRule.create({
            'name': 'Net Salary',
            'code': 'NET',
            'sequence': 200,
            'struct_id': self.payroll_structure.id,
            'category_id': self.base_salary_rule_category.id,
            'condition_select': 'none',
            'amount_select': 'code',
            'amount_python_compute':
            ('result = categories.BASIC + categories.ALW + categories.DED'),
            'salary_rule_account_ids': self.net_salary_rule_account_lines
        })

        self.stage_approved = self.env.ref(
            'bits_hr_payroll_news.stage_payroll_news2')

        self.contract = self.hr_contract.create({
            'name': "Test Contract",
            'structure_type_id': self.payroll_structure_type.id,
            'employee_id': self.employee.id,
            'date_start': date(2020, 1, 1),
            'wage_type': "monthly",
            'wage': 2800000,
        })

        self.contract_01 = self.hr_contract.create({
            'name': "Test Contract",
            'structure_type_id': self.payroll_structure_type.id,
            'employee_id': self.employee_1.id,
            'date_start': date(2020, 1, 1),
            'wage_type': "monthly",
            'wage': 3800000,
            'state': "open"
        })

        self.payroll_new = self.hr_payroll_new.create({
            'name': "Test News",
            'payroll_structure_id': self.payroll_structure_01.id,
            'salary_rule_id': self.others_discounts.id,
            'user_id': self.env.user.id,
            'date_start': date(2020, 1, 1),
            'date_end': date(2020, 1, 31),
            'employee_payroll_news_ids': [(0, 0, {
                'employee_id': self.employee_1.id,
                'quantity': 3,
                'amount': -14583
            })],
            'stage_id': self.stage_approved.id
        })

        self.payroll_new_01 = self.hr_payroll_new.create({
            'name': "Test News 01",
            'payroll_structure_id': self.payroll_structure_01.id,
            'salary_rule_id': self.others_discounts.id,
            'user_id': self.env.user.id,
            'date_start': date(2020, 1, 1),
            'date_end': date(2020, 1, 31),
            'employee_payroll_news_ids': [(0, 0, {
                'employee_id': self.employee_1.id,
                'quantity': 3,
                'amount': -14583
            })],
            'stage_id': self.stage_approved.id
        })

        self.payslip = self.hr_payslip.create({
            'name': "Payroll Test",
            'date_from': date(2020, 1, 1),
            'date_to': date(2020, 1, 31),
            'employee_id': self.employee.id,
            'contract_id': self.contract.id
        })

        self.payslip_01 = self.hr_payslip.create({
            'name': "Payroll Test 1",
            'date_from': date(2020, 1, 1),
            'date_to': date(2020, 1, 31),
            'employee_id': self.employee_1.id,
            'contract_id': self.contract_01.id
        })

        self.payslip_02 = self.hr_payslip.create({
            'name': "Payroll Test 2",
            'date_from': date(2020, 1, 1),
            'date_to': date(2020, 1, 31),
            'employee_id': self.employee_1.id,
            'contract_id': self.contract_01.id,
            'struct_id': self.payroll_structure.id,
            'state': 'verify',
            'general_state': 'sent'
        })
        self.work_entry_type = self.HrWorkEntryType.search([
            ('code', '=', 'WORK100')
        ], limit=1)

        self.worked_days = self.HrPayslipWorkedDays.create({
            'work_entry_type_id': self.work_entry_type.id,
            'sequence': 25,
            'number_of_hours': 184.00,
            'name': self.work_entry_type.name,
            'number_of_days': 30.00,
            'contract_id': self.contract.id,
            'amount': self.contract.wage,
            'payslip_id': self.payslip_02.id
        })

    def test_generate_line_parafiscal(self):
        self.payslip_02.write({
            'general_state': "approved"
        })
        self.payslip_02.compute_sheet()
        for view in self.payslip_02.line_ids:
            view.write({'total': round(view.total)})

        self.payslip_02.action_payslip_done()
        self.payslip_02._get_validate_sign_value(-100)
