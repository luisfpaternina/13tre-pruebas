from datetime import datetime, timedelta, date
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestHrPayslip(TransactionCase):

    def setUp(self):
        super(TestHrPayslip, self).setUp()
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
        self.HrResPartner = self.env['res.partner']
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

        self.employee = self.hr_employee.create({
            'name': "Juan Perez"
        })
        self.employee_1 = self.hr_employee.create({
            'name': "Mario Perez"
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
        })
        self.payroll_structure_01 = self.HrPayrollStructure.create({
            'name': 'Structures Test 01',
            'type_id': self.payroll_structure_type_01.id,
        })
        self.base_salary_rule_category = self.HrSalaryRuleCategory.create({
            'name': 'BASIC',
            'code': 'BASIC'
        })
        self.base_salary_rule_category_01 = self.HrSalaryRuleCategory.create({
            'name': 'Deducciones',
            'code': 'DED'
        })

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
            'affect_payslip': True
        })

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
            'amount_percentage': 0.5220
        })

        self.aporte_salud_rule = self.HrSalaryRule.create({
            'name': 'APORTE SALUD',
            'code': '3010',
            'sequence': 180,
            'struct_id': self.payroll_structure.id,
            'category_id': self.base_salary_rule_category.id,
            'condition_select': 'none',
            'amount_select': 'percentage',
            'amount_percentage_base': 'payslip.paid_amount',
            'amount_percentage': -4.0000
        })

        self.aporte_pension_rule = self.HrSalaryRule.create({
            'name': 'APORTE PENSION',
            'code': '3020',
            'sequence': 180,
            'struct_id': self.payroll_structure.id,
            'category_id': self.base_salary_rule_category.id,
            'condition_select': 'none',
            'amount_select': 'percentage',
            'amount_percentage_base': 'payslip.paid_amount',
            'amount_percentage': -4.0000
        })
        # aporte pension end

        self.aporte_fondo_solidario_rule = self.HrSalaryRule.create({
            'name': 'APORTE FONDO SOLIDARIO',
            'code': '3023',
            'sequence': 170,
            'struct_id': self.payroll_structure.id,
            'category_id': self.base_salary_rule_category.id,
            'condition_select': 'none',
            'amount_select': 'percentage',
            'amount_percentage_base': 'payslip.paid_amount',
            'amount_percentage': -1.0000
        })

        self.others_discounts = self.HrSalaryRule.create({
            'name': 'Otros descuentos',
            'code': '3305',
            'sequence': 129,
            'struct_id': self.payroll_structure_01.id,
            'category_id': self.base_salary_rule_category_01.id,
            'condition_select': 'none',
            'amount_select': 'fix',
            'quantity': '1',
            'amount_fix': -200000
        })

        self.net_salary_rule = self.HrSalaryRule.create({
            'name': 'Net Salary',
            'code': 'NET',
            'sequence': 200,
            'struct_id': self.payroll_structure.id,
            'category_id': self.base_salary_rule_category.id,
            'condition_select': 'none',
            'amount_select': 'code',
            'amount_python_compute':
            ('result = categories.BASIC + categories.ALW + categories.DED')
        })

        # Estado para la aprobacion de las novedades
        self.stage_approved = self.env.ref(
            'bits_hr_payroll_news.stage_payroll_news2')
        
        # Contrato para el empleado Juan Perez
        self.contract = self.hr_contract.create({
            'name': "Test Contract",
            'structure_type_id': self.payroll_structure_type.id,
            'employee_id': self.employee.id,
            'date_start': date(2020, 1, 1),
            'wage_type': "monthly",
            'wage': 2800000,
        })
        
        # Contrato para el empleado Mario Perez
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

        self.payroll_new_01 = self.hr_payroll_new.create({
            'name': "Test News 01",
            'payroll_structure_id': self.salary_structure_01.id,
            'salary_rule_id': self.salary_rule_01.id,
            'user_id': self.env.user.id,
            'date_start': date(2020, 1, 1),
            'date_end': date(2020, 1, 31),
            'employee_payroll_news_ids': [(0, 0, {
                'employee_id': self.employee.id,
                'quantity': 3,
                'amount': 14583
            })],
            'stage_id': self.stage_approved.id
        })
        
        # Nomina para Juan Perez
        self.payslip = self.hr_payslip.create({
            'name': "Payroll Test",
            'date_from': date(2020, 1, 1),
            'date_to': date(2020, 1, 31),
            'employee_id': self.employee.id,
            'contract_id': self.contract.id
        })
        
        # Nomina para Mario Perez
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

    def test_add_salary_rule(self):
        self.payslip_02.compute_sheet()
        for line in self.payslip_02.line_ids:
            line._compute_total()
            line.write({'total': round(line.total)})

    def test_approve_payroll(self):
        self.payslip_02.compute_sheet()
