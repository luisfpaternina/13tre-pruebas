from odoo.exceptions import ValidationError
from .test_bits_hr_payroll_news import (TestBitsHrPayrollNews)


class TestHrPayslip(TestBitsHrPayrollNews):

    def setUp(self):
        super(TestHrPayslip, self).setUp()

    def test_get_payslip_lines(self):
        self.payslip._get_payslip_lines()

        self.payroll_new.write({
            'salary_rule_id': self.salary_rule_4.id
        })
        self.salary_rule.unlink()
        self.payslip._get_payslip_lines()

    def test_get_payslip_lines_change_code_rule(self):
        rule = self.hr_salary_rule.search([('code', '=', 'BASIC')])
        rule.write({
            'code': "BASICO"
        })
        self.payslip._get_payslip_lines()

        rule_0 = self.hr_salary_rule.search([('code', '=', 'GROSS')])
        rule_0.write({
            'code': "BRUTO"
        })
        self.payslip._get_payslip_lines()

        rule_1 = self.hr_salary_rule.search([('code', '=', 'NET')])
        rule_1.write({
            'code': "NETO"
        })
        self.payslip._get_payslip_lines()

    def test_compute_sheet(self):
        self.payslip.compute_sheet()

    def test_compute_total(self):
        salary = 4000000
        days = 30
        self.payslip.compute_sheet()
        line = self.env['hr.payslip.line'].search([
            ('slip_id', '=', self.payslip.id),
            ('code', '=', 'BASIC')
        ])
        line.write({
            'quantity': days,
            'amount': salary/days,
            'rate': 100
        })
        line._compute_total()
        self.assertEqual(line.total, salary)

    def test_config_integrate_payslip(self):
        rest = list(self.payslip._get_payslip_lines())
        config = self.env['res.config.settings'].create({})
        config.integrate_payroll_news = True
        config.execute()

        rest2 = list(self.payslip._get_payslip_lines())
        # self.assertTrue(len(rest2) > len(rest))

    def test_config_integrate_salary_extra(self):
        config = self.env['res.config.settings'].create({})
        config.module_bits_hr_contract_advance = True
        config.execute()

    def test_non_constitutive_payslip(self):
        data = {
            'name': "BONO 01",
            'code': "BON01",
            'sequence': 30,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'non_constitutive_calculate': True,
            'affect_payslip': True,
            'non_const_percentage_up': 40.0,
            'constitutive': 'non_const',
            'quantity': 1.0,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 6000000,
            'apply_other_rules': 'ERROR,FALTA,NOEXIST',
        }
        bono1 = self.hr_salary_rule.create(data)

        data['name'] = "BONO 02 Extra legal, NOT (no-const, const)"
        data['code'] = "BON02"
        data['constitutive'] = 'none'
        data['non_const_percentage_up'] = 0
        data['constitutive_calculate'] = True
        data['apply_other_rules'] = 'BON01,CAJA,PENS'
        data['exclude_in'] = 'amount'
        data['exclude_other_rules'] = 'BON01,CAJA,PENS'

        bono2 = self.hr_salary_rule.create(data)

        # Test exlude IBC
        data['name'] = "Exclude IBC"
        data['code'] = "suma-ibc"
        data['constitutive'] = 'none'
        data['non_const_percentage_up'] = 0
        data['quantity'] = 0
        data['amount_fix'] = 1
        data['constitutive_calculate'] = True
        data['benefit_calculate'] = False
        data['exclude_in'] = 'total'
        data['exclude_other_rules'] = 'BON01,CAJA,PENS'
        del data['apply_other_rules']
        exlude_ibc = self.hr_salary_rule.create(data)

        data['code'] = "BON03"
        data['constitutive'] = 'non_const'
        data['non_const_percentage_up'] = 40.0
        data['apply_other_rules'] = 'ERROR,FALTA,NOEXIST'
        del data['constitutive_calculate']
        bono3 = self.hr_salary_rule.create(data)
        rest2 = list(self.payslip._get_payslip_lines())

        data['code'] = "EXEDENT"
        data['constitutive'] = 'is_const'
        data['non_const_percentage_up'] = 40.0
        data['quantity'] = 1
        data['amount_fix'] = 30000000
        data['not_remunerate'] = True
        data['affect_worked_days'] = True
        data['apply_other_rules'] = 'ERROR,FALTA,NOEXIST'
        bono3 = self.hr_salary_rule.create(data)
        rest2 = list(self.payslip._get_payslip_lines())
        del data['not_remunerate']
        del data['affect_worked_days']

        data['name'] = "Sub transporte"
        data['code'] = "120"
        data['constitutive'] = 'none'
        data['non_const_percentage_up'] = 0
        data['quantity'] = 0
        data['amount_fix'] = 1
        data['constitutive_calculate'] = True
        data['benefit_calculate'] = False
        data['exclude_in'] = 'total'
        data['exclude_other_rules'] = 'BON01,CAJA,PENS'
        del data['apply_other_rules']

        bono4 = self.hr_salary_rule.create(data)
        rest2 = list(self.payslip._get_payslip_lines())

    def test_get_rounding_rule(self):
        rule = self.hr_salary_rule.search(
            [('code', '=', 'BASIC')], limit=1)
        config = self.env['res.config.settings'].create({})
        config.rounding_rule_ids = rule.ids
        config.execute()
        salary = 963400.0
        days = 30
        self.payslip.compute_sheet()
        line = self.env['hr.payslip.line'].search([
            ('slip_id', '=', self.payslip.id),
            ('code', '=', 'BASIC')
        ])
        line.write({
            'quantity': days,
            'amount': 32112,
            'rate': 100
        })
        line._compute_total()
        self.assertEqual(line.total, salary)

    def test_compute_field(self):
        self.payslip._compute_commission()

    def test_validate_contract_change(self):
        config = self.env['res.config.settings'].create({})
        self.env['ir.config_parameter'].sudo()\
            .set_param('module_bits_hr_contract_advance', True)
        config.execute()

        salary_structure_1 = self.env.ref(
            'bits_hr_payroll_news.hr_payroll_structure_type_employee_02')
        salary_structure_2 = self.env.ref(
            'bits_hr_payroll_news.hr_payroll_structure_type_employee_04')
        payroll_structure = self.env.ref(
            'bits_hr_payroll_news.hr_payroll_structure_employee_04')
        employee = self.hr_employee.create({
            'name': "SENA TEST",
            'identification_id': "75395146"
        })
        new_contract = self.hr_contract.create({
            'name': "Contract Test 3",
            'rate': 4.3500,
            'date_start': '2021-02-19',
            'structure_type_id': salary_structure_2.id,
            'wage': 800000,
            'state': 'open',
            'employee_id': employee.id
        })
        old_contract = self.hr_contract.create({
            'name': "Contract Test 2",
            'rate': 4.3500,
            'date_start': '2020-01-10',
            'date_end': '2021-02-19',
            'structure_type_id': salary_structure_1.id,
            'wage': 800000,
            'state': 'cancel',
            'employee_id': employee.id
        })
        payslip = self.hr_payslip.create({
            'name': "Payroll Test",
            'employee_id': employee.id,
            'contract_id': new_contract.id,
            'struct_id': payroll_structure.id,
            'date_from': '2021-02-01',
            'date_to': '2021-02-28',
        })
        payslip1 = self.hr_payslip.create({
            'name': "Payroll Test",
            'employee_id': employee.id,
            'contract_id': new_contract.id,
            'struct_id': self.payroll_structure.id,
            'date_from': '2021-02-01',
            'date_to': '2021-02-28',
        })

        payslip.compute_sheet()
        payslip1.compute_sheet()
