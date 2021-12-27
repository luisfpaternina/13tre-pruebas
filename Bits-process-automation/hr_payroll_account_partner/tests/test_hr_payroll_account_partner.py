from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta

import logging


class TesHrPayrollAccountPartner(TransactionCase):

    def setUp(self):
        super(TesHrPayrollAccountPartner, self).setUp()

        self.HrPayslip = self.env['hr.payslip']
        self.HrPayslipWorkedDays = self.env['hr.payslip.worked_days']
        self.HrPayslipLine = self.env['hr.payslip.line']
        self.HrEmployee = self.env['hr.employee']
        self.HrEmployeeCenterCost = self.env['hr.employee.center.cost']
        self.HrResPartner = self.env['res.partner']
        self.HrPayrollStructure = self.env['hr.payroll.structure']
        self.HrPayrollStructureType = self.env['hr.payroll.structure.type']
        self.HrSalaryRule = self.env['hr.salary.rule']
        self.HrSalaryRuleAccount = self.env['hr.salary.rule.account']
        self.HrSalaryRuleCategory = self.env['hr.salary.rule.category']
        self.HrWorkEntryType = self.env['hr.work.entry.type']
        self.AccountAnalyticAccount = self.env['account.analytic.account']
        self.AccountMove = self.env['account.move']
        self.AccountMoveLine = self.env['account.move.line']
        self.AccountAccount = self.env['account.account']
        self.AccountAccountType = self.env['account.account.type']
        self.HrContract = self.env['hr.contract']
        self.AccountJournal = self.env['account.journal']
        self.SocialSecurity = self.env['social.security']
        self.company = self.env.company
        self.precision = self.env['decimal.precision'].precision_get('Payroll')
        self.company.write({
            'account_type_expense': True
        })
        self.social_security_pension = self.SocialSecurity.create({
            'code': 'EPS011',
            'name': "Test Entity",
            'entity_type': "pension"
        })

        self.contact = self.HrResPartner.create({
            'name': 'partner name'
        })

        self.account_account_type_benefit = self.AccountAccountType.create({
            'name': 'Beneficios a empleados',
            'type': 'other',
            'internal_group': 'liability'
        })

        # ME SIRVE
        self.payroll_structure_type = self.HrPayrollStructureType.create({
            'name': 'Structure type test',
            'wage_type': 'monthly',
            # 'is_novelty': True
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
            'default_credit_account_id': self.account_account_wage.id,
            'default_debit_account_id': self.account_account_wage.id
        })

        # ME SIRVE
        self.payroll_structure = self.HrPayrollStructure.create({
            'name': 'Structures Test',
            'type_id': self.payroll_structure_type.id,
            'journal_id': self.account_journal.id
        })

        self.occasional_structure = self.HrPayrollStructure.create({
            'name': 'Occasional structure',
            'type_id': self.payroll_structure_type.id,
            'journal_id': self.account_journal.id
        })

        self.payroll_structure_two = self.HrPayrollStructure.create({
            'name': 'Structure Two',
            'type_id': self.payroll_structure_type.id,
            'journal_id': self.account_journal.id
        })

        self.center_cost = self.AccountAnalyticAccount.create({
            'name': 'Desarrollo',
            'code': 'dev'
        })
        self.center_cost_1 = self.AccountAnalyticAccount.create({
            'name': 'Gestion Comercial',
            'code': 'GCO'
        })

        self.contract = self.HrContract.create({
            'name': 'contract example',
            'date_start': datetime.now(),
            'date_end': datetime.now()+timedelta(days=365),
            'wage': 2800000,
            'structure_type_id': self.payroll_structure_type.id
        })
        self.contract_1 = self.HrContract.create({
            'name': 'contract example',
            'date_start': datetime.now(),
            'date_end': datetime.now()+timedelta(days=365),
            'wage': 2800000,
            'structure_type_id': self.payroll_structure_type.id
        })

        self.employee = self.HrEmployee.create({
            'name': 'Employee Test',
            'names': 'Employee full name',
            'surnames': 'Employee surnames',
            'known_as': 'Employee Known',
            'contract_id': self.contract.id,
            'document_type': '13',
            'identification_id': "78945612",
            'address_home_id': self.contact.id
        })

        self.employee_whitout_partner = self.HrEmployee.create({
            'name': 'Employee Whitout Partner',
            'names': 'Employee full name',
            'surnames': 'Employee surnames',
            'known_as': 'Employee Known',
            'contract_id': self.contract_1.id,
            'document_type': '13',
            'identification_id': "965232124"
        })
        self.contract_1 = self.HrContract.create({
            'name': 'contract example',
            'date_start': datetime.now(),
            'date_end': datetime.now()+timedelta(days=365),
            'wage': 2800000,
            'structure_type_id': self.payroll_structure_type.id,
            'employee_id': self.employee_whitout_partner.id
        })

        self.center_costo_employee = self.HrEmployeeCenterCost.create({
            'percentage': 100.00,
            'employee_id': self.employee.id,
            'account_analytic_id': self.center_cost.id
        })

        self.account_account_type = self.AccountAccountType.create({
            'name': 'Gastos de administración',
            'type': 'other',
            'internal_group': 'expense'
        })

        self.account_account = self.AccountAccount.create({
            'code': '5105950499',
            'name': 'AUXILIO DE ALIMENTACION - NCS',
            'user_type_id': self.account_account_type.id
        })

        self.account_move = self.AccountMove.create({
            'ref': 'Nomina Test',
            'date': datetime.now(),
            'journal_id': self.account_journal.id,
            # 'line_ids': self.move_list
        })

        # SPRINT 2.0 TEST; un nuevo comienzo
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

        self.account_others_disscount = self.AccountAccount.create({
            'code': '13659503',
            'name': 'OTROS DESCUENTOS',
            'user_type_id': self.account_account_type.id
        })

        self.account_fondo_solidario = self.AccountAccount.create({
            'code': '23803005',
            'name': 'APORTE FONDO SOLIDATIO',
            'user_type_id': self.account_account_type.id
        })

        self.base_salary_rule_category = self.HrSalaryRuleCategory.create({
            'name': 'BASIC',
            'code': 'BASIC'
        })

        # Regla salarial salario base begin
        self.base_salary_rule_account_lines = [
            (0, 0, {
                'account_account_id': self.account_salary_dev.id,
                'account_analytic_id': self.center_cost.id,
                'account_type': 'debit'
            })
        ]

        self.base_salary_rule = self.HrSalaryRule.create({
            'name': 'Salario Base',
            'code': 'BASIC',
            'import_code': 'BASIC',
            'sequence': 1,
            'struct_id': self.payroll_structure.id,
            'category_id': self.base_salary_rule_category.id,
            'condition_select': 'none',
            'amount_select': 'percentage',
            'quantity':
            ('worked_days.WORK100 and worked_days.WORK100.number_of_days'),
            'amount_fix': 1.00,
            'amount_percentage': 100.0000,
            'amount_python_compute': 100.0000,
            'amount_percentage_base': 'contract.wage/30',
            'condition_range': 'contract.wage',
            'note': 'sueldo / 30 x dias trabajados',
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
            'applies_all_cost_center': True,
            'amount_percentage': -1.0000,
            'salary_rule_account_ids': self.aporte_fondo_solidario_lines
        })

        # otros descuentos
        self.others_discounts_lines = [
            (0, 0, {
                'account_account_id': self.account_others_disscount.id,
                'account_analytic_id': self.center_cost.id,
                'account_type': 'credit'
            }),
            (0, 0, {
                'account_account_id': self.account_others_disscount.id,
                'account_analytic_id': self.center_cost.id,
                'account_type': 'debit'
            })
        ]

        self.others_discounts = self.HrSalaryRule.create({
            'name': 'Otros descuentos',
            'code': '3305',
            'sequence': 129,
            'struct_id': self.payroll_structure.id,
            'category_id': self.base_salary_rule_category.id,
            # 'applies_all_cost_center': True,
            'condition_select': 'none',
            'amount_select': 'fix',
            'quantity': '1',
            'amount_fix': -200000,
            'salary_rule_account_ids': self.others_discounts_lines
        })

        self.net_salary_rule_whitout_lines = self.HrSalaryRule.create({
            'name': 'Net Salary Without lines',
            'code': 'NET',
            'sequence': 200,
            'struct_id': self.payroll_structure_two.id,
            'category_id': self.base_salary_rule_category.id,
            'condition_select': 'none',
            'amount_select': 'code',
            'amount_python_compute':
            ('result = categories.BASIC + categories.ALW + categories.DED'),
        })

        self.aporte_salud_whitout_lines = self.HrSalaryRule.create({
            'name': 'APORTE SALUD whitout lines',
            'code': '3010',
            'sequence': 180,
            'struct_id': self.payroll_structure_two.id,
            'category_id': self.base_salary_rule_category.id,
            'condition_select': 'none',
            'amount_select': 'code',
            'amount_python_compute':
            ('result = categories.BASIC + categories.ALW + categories.DED'),
        })

        self.aporte_pension_whitout_lines = self.HrSalaryRule.create({
            'name': 'APORTE PENSION cc',
            'code': '3020',
            'sequence': 180,
            'struct_id': self.payroll_structure_two.id,
            'category_id': self.base_salary_rule_category.id,
            'condition_select': 'none',
            'amount_select': 'percentage',
            'amount_percentage_base': 'payslip.paid_amount',
            'amount_percentage': -4.0000
        })

        self.aporte_fondo_solidario_whithout_lines = self.HrSalaryRule.create({
            'name': 'APORTE FONDO SOLIDARIO WITHOUT LINES',
            'code': '3023',
            'sequence': 170,
            'struct_id': self.payroll_structure_two.id,
            'category_id': self.base_salary_rule_category.id,
            'condition_select': 'none',
            'amount_select': 'percentage',
            'amount_percentage_base': 'payslip.paid_amount',
            'amount_percentage': -1.0000
        })

        self.paylisp = self.HrPayslip.create({
            'name': 'Paylisp Test',
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'struct_id': self.payroll_structure.id,
            'date_from': datetime.now(),
            'date_to': datetime.now() + timedelta(days=30),
            'move_id': self.account_move.id
        })

        self.paylisp_whitout_partner = self.HrPayslip.create({
            'name': 'Paylisp Test 2',
            'employee_id': self.employee_whitout_partner.id,
            'contract_id': self.contract_1.id,
            'struct_id': self.payroll_structure.id,
            'date_from': datetime.now(),
            'date_to': datetime.now() + timedelta(days=30),
            'move_id': self.account_move.id,
        })

        self.paylisp_netsalary_whitout_lines = self.HrPayslip.create({
            'name': 'Paylisp Test 3',
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'struct_id': self.payroll_structure_two.id,
            'date_from': datetime.now(),
            'date_to': datetime.now() + timedelta(days=30),
            'move_id': self.account_move.id,
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
            'payslip_id': self.paylisp.id
        })

    # Test success
    def test_success(self):
        self.paylisp.compute_sheet()
        for view in self.paylisp.line_ids:
            view.write({'total': round(view.total)})

        self.paylisp.action_payslip_done()

    # Test whitout partner
    def test_payslip_whitout_partner(self):
        self.paylisp_whitout_partner.compute_sheet()

        with self.assertRaises(ValidationError):
            self.paylisp_whitout_partner.action_payslip_done()

    # Test whitout center cost
    def test_payslip_whitout_ce_cost(self):

        self.employee_whitout_partner.write({
            'address_home_id': self.contact.id
        })

        self.paylisp_whitout_partner.compute_sheet()

        with self.assertRaises(ValidationError):
            self.paylisp_whitout_partner.action_payslip_done()

    # Test float_is_zero validation how True

    # def test_float_is_zero_true(self):
    #     self.employee_whitout_partner.write({
    #         'address_home_id': self.contact.id
    #     })
    #     self.HrEmployeeCenterCost.create({
    #         'porcentage': 100.00,
    #         'employee_id': self.employee_whitout_partner.id,
    #         'account_analytic_id': self.center_cost.id
    #     })
    #     self.net_salary_rule.write({
    #         'salary_rule_account_ids': []
    #     })

    #     self.paylisp_whitout_partner.compute_sheet()

    #     with self.assertRaises(ValidationError):
    #         self.paylisp_whitout_partner.action_payslip_done()

    def test_payslip_whitout_netsalary_lines(self):
        self.paylisp_netsalary_whitout_lines.compute_sheet()
        self.paylisp_netsalary_whitout_lines.action_payslip_done()

    def test_get_account_cost_center(self):
        self.others_discounts.write({
            'applies_all_cost_center': True
        })
        self.paylisp.compute_sheet()
        for view in self.paylisp.line_ids:
            view.write({'total': round(view.total)})
        self.paylisp.action_payslip_done()

    def test_get_account_parafiscal(self):
        self.employee.write({
            'pension': self.social_security_pension.id
        })
        self.aporte_pension_rule.salary_rule_account_ids[0].write({
            'social_security_id': self.social_security_pension.id
        })
        self.aporte_pension_rule.write({
            'search_parafiscales': True
        })
        self.paylisp.compute_sheet()
        for view in self.paylisp.line_ids:
            view.write({'total': round(view.total)})
        self.paylisp.action_payslip_done()

    def test_paylip_line(self):
        self.aporte_fondo_solidario_rule.write({
            'quantity': 0.0
        })
        self.paylisp.compute_sheet()
        for view in self.paylisp.line_ids:
            view.write({'total': round(view.total)})
            if self.aporte_fondo_solidario_rule.id == view.salary_rule_id.id:
                view.write({'amount': 0.0})
        self.paylisp.action_payslip_done()

    def test_get_account_cost_center_witout_accounts(self):
        self.others_discounts.write({
            'applies_all_cost_center': True,
            'salary_rule_account_ids': False
        })
        self.paylisp.compute_sheet()
        for view in self.paylisp.line_ids:
            view.write({'total': round(view.total)})
        self.paylisp.action_payslip_done()

    def test_default_account_account(self):
        self.paylisp.compute_sheet()
        self.paylisp.default_account_account(
            self.aporte_fondo_solidario_rule, 'debit')

    def test_get_account_parafiscal_without_entity(self):
        self.paylisp.compute_sheet()
        self.paylisp.get_account_parafiscal(
            self.aporte_pension_rule, [])

    def test_get_account_credit_move(self):
        self.paylisp.compute_sheet()
        self.paylisp._get_account_credit_move(
            self.aporte_salud_whitout_lines, False)

    def test_generate_line_parafiscal(self):
        self.employee.write({
            'pension': self.social_security_pension.id
        })
        self.arl_salary_rule.write({
            'search_parafiscales': True
        })
        for account_rule in self.arl_salary_rule.salary_rule_account_ids:
            account_rule.write({
                'social_security_id': self.social_security_pension.id
            })
        self.paylisp.compute_sheet()
        for view in self.paylisp.line_ids:
            view.write({'total': round(view.total)})
        self.paylisp.action_payslip_done()

    def test_generate_line_parafiscal_without_credit_account(self):
        self.employee.write({
            'pension': self.social_security_pension.id
        })
        self.arl_salary_rule.write({
            'search_parafiscales': True
        })
        credit_account = False
        for account_rule in self.arl_salary_rule.salary_rule_account_ids:
            account_rule.write({
                'social_security_id': self.social_security_pension.id
            })
            if account_rule.account_type == 'credit':
                credit_account = account_rule
        credit_account.unlink()
        self.paylisp.compute_sheet()
        for view in self.paylisp.line_ids:
            view.write({'total': round(view.total)})
        self.paylisp.action_payslip_done()

    def test_get_account_parafiscal_rule(self):
        self.employee.write({
            'pension': self.social_security_pension.id
        })
        self.arl_salary_rule.write({
            'search_parafiscales': True
        })
        for account_rule in self.arl_salary_rule.salary_rule_account_ids:
            account_rule.write({
                'social_security_id': self.social_security_pension.id
            })
        self.paylisp.compute_sheet()
        self.paylisp.get_account_parafiscal(self.aporte_salud_whitout_lines,
                                            self.social_security_pension)

    def test_validate_account_account_journal(self):
        self.employee.write({
            'pension': self.social_security_pension.id
        })
        self.arl_salary_rule.write({
            'search_parafiscales': True
        })
        for account_rule in self.arl_salary_rule.salary_rule_account_ids:
            account_rule.write({
                'social_security_id': self.social_security_pension.id
            })
        self.paylisp.compute_sheet()
        self.account_journal.write({
            'default_credit_account_id': False
        })
        with self.assertRaises(UserError):
            self.paylisp._validate_account_account_journal(False, self.paylisp)

    def test_get_line_adjustment_entry(self):
        self.account_journal.write({
            'default_debit_account_id': self.account_account_wage.id
        })
        self.paylisp.compute_sheet()
        self.paylisp.action_payslip_done()

    def test_validate_social_social_security(self):
        self.paylisp._validate_social_social_security(self.arl_salary_rule)

    def test_validate_analytic_account_account(self):
        self.paylisp._validate_analytic_account_account(self.arl_salary_rule)

    def test_validate_division_center_cost(self):
        self.employee.write({
            'pension': self.social_security_pension.id
        })
        self.aporte_pension_rule.write({
            'salary_rule_account_ids': False,
            'search_parafiscales': True,
            'applies_all_cost_center': True
        })
        self.HrSalaryRuleAccount.create({
            'salary_rule_id': self.aporte_pension_rule.id,
            'account_analytic_id': self.center_cost.id,
            'account_account_id': self.account_account.id,
            'account_type': 'debit'
        })
        self.HrSalaryRuleAccount.create({
            'salary_rule_id': self.aporte_pension_rule.id,
            'social_security_id': self.social_security_pension.id,
            'account_account_id': self.account_account.id,
            'account_type': 'credit'
        })
        self.paylisp.compute_sheet()
        for view in self.paylisp.line_ids:
            view.write({'total': round(view.total)})

        self.paylisp.action_payslip_done()

    def test_validate_rules_for_pr(self):
        self.employee.write({
            'pension': self.social_security_pension.id
        })
        self.aporte_pension_rule.write({
            'search_parafiscales': True
        })
        self.HrSalaryRuleAccount.create({
            'salary_rule_id': self.aporte_pension_rule.id,
            'social_security_id': self.social_security_pension.id,
            'account_account_id': self.account_account.id,
            'account_type': 'debit'
        })
        self.paylisp.compute_sheet()
        for view in self.paylisp.line_ids:
            view.write({'total': round(view.total)})

        self.paylisp.action_payslip_done()

    def test_validate_rules_for_pr_cc(self):
        self.aporte_pension_rule.write({
            'applies_all_cost_center': True
        })
        self.HrSalaryRuleAccount.create({
            'salary_rule_id': self.aporte_pension_rule.id,
            'account_analytic_id': self.center_cost.id,
            'account_account_id': self.account_account.id,
            'account_type': 'debit'
        })
        self.paylisp.compute_sheet()
        for view in self.paylisp.line_ids:
            view.write({'total': round(view.total)})

        self.paylisp.action_payslip_done()

    def test_validate_division_center_cost_without_config(self):
        self.company.write({
            'account_type_expense': False
        })
        self.employee.write({
            'pension': self.social_security_pension.id
        })
        self.aporte_pension_rule.write({
            'salary_rule_account_ids': False,
            'search_parafiscales': True,
            'applies_all_cost_center': True
        })
        self.HrSalaryRuleAccount.create({
            'salary_rule_id': self.aporte_pension_rule.id,
            'account_analytic_id': self.center_cost.id,
            'account_account_id': self.account_account.id,
            'account_type': 'debit'
        })
        self.HrSalaryRuleAccount.create({
            'salary_rule_id': self.aporte_pension_rule.id,
            'social_security_id': self.social_security_pension.id,
            'account_account_id': self.account_account.id,
            'account_type': 'credit'
        })
        self.paylisp.compute_sheet()
        for view in self.paylisp.line_ids:
            view.write({'total': round(view.total)})

        self.paylisp.action_payslip_done()

    def test_get_line_adjustment_entry_validate(self):
        self.paylisp.get_line_adjustment_entry(
            180000, 200000, self.precision, self.paylisp, False,
            self.contact, '2021-03-15', [])

    def test_create_salary_rule_account_analytic(self):
        vals = {
            'salary_rule_code': 'BASIC',
            'account_code': '2505010199'
        }

        vals['account_type'] = 'debit'
        vals['analytic_code'] = 'dev'
        self.HrSalaryRuleAccount.create(vals)
        logging.warning('The vals 1 %s', vals)

    def test_create_salary_rule_account_social_security(self):
        vals = {
            'salary_rule_code': 'BASIC',
            'account_code': '2505010199'
        }
        vals['account_type'] = 'credit'
        vals['social_security_code'] = 'EPS001'
        self.HrSalaryRuleAccount.create(vals)
        logging.warning('The vals 2 %s', vals)

    def test_create_salary_rule_account_minimal(self):
        vals = {
            'salary_rule_code': 'BASIC',
            'account_code': '2505010199'
        }
        vals['account_type'] = 'debit'
        self.HrSalaryRuleAccount.create(vals)
        logging.warning('The vals 3 %s', vals)
