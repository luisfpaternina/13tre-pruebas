from datetime import datetime, date
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestHrPayslip(TransactionCase):

    def setUp(self):
        super(TestHrPayslip, self).setUp()
        self.hr_employee = self.env['hr.employee']
        self.hr_payroll_structure = self.env['hr.payroll.structure']
        self.hr_salary_rule = self.env['hr.salary.rule']
        self.hr_payroll_structure_type = self.env['hr.payroll.structure.type']
        self.hr_salary_rule = self.env['hr.salary.rule']
        self.hr_salary_rule_category = self.env['hr.salary.rule.category']
        self.hr_contract = self.env['hr.contract']
        self.hr_payslip = self.env['hr.payslip']
        self.hr_work = self.env['hr.work.entry']
        self.hr_work_type = self.env['hr.work.entry.type']

        self.employee = self.hr_employee.create({
            'name': "Juan Perez"
        })
        self.employee_1 = self.hr_employee.create({
            'name': "Mario Perez"
        })

        self.structure_type = self.hr_payroll_structure_type.create({
            'name': "Test Type",
            'wage_type': "monthly"
        })
        self.payroll_structure = self.hr_payroll_structure.create({
            'name': "Structure Test",
            'type_id': self.structure_type.id
        })
        self.salary_rule_category = self.hr_salary_rule_category.create({
            'name': "Salary Category Test",
            'code': "SCT"
        })

        self.contract = self.hr_contract.create({
            'name': "Test Contract",
            'structure_type_id': self.structure_type.id,
            'employee_id': self.employee.id,
            'date_start': date(2020, 1, 1),
            'wage_type': "monthly",
            'wage': 2800000,
            'state': "open"
        })
        self.payslip = self.hr_payslip.create({
            'name': "Payroll Test",
            'date_from': date(2020, 1, 1),
            'date_to': date(2020, 1, 31),
            'employee_id': self.employee.id,
            'contract_id': self.contract.id
        })

    def test_onchange_employee(self):
        extra_hours = self.hr_work_type.search([('code', '=', 'WORK300')])
        self.hr_work.create({
            'name': "Test Entry",
            'employee_id': self.employee.id,
            'work_entry_type_id': extra_hours.id,
            'date_start': datetime(2020, 1, 15, 19, 0, 0),
            'date_stop': datetime(2020, 1, 15, 23, 0, 0)
        })
        self.payslip._onchange_employee()

    def test_onchange_employee_not_contract(self):
        self.structure_type.write({
            'wage_type': "hourly"
        })
        contract_new = self.hr_contract.create({
            'name': "Test Contract 1",
            'structure_type_id': self.structure_type.id,
            'employee_id': self.employee_1.id,
            'date_start': date(2020, 2, 1),
            'wage_type': "hourly",
            'wage': 28000,
            'state': "open"
        })
        payslip_new = self.hr_payslip.create({
            'name': "Payroll Test 1",
            'date_from': date(2020, 2, 1),
            'date_to': date(2020, 2, 29),
            'employee_id': self.employee_1.id,
            'contract_id': contract_new.id
        })
        payslip_new._onchange_employee()

    def test_onchange_value_worked_days(self):
        self.payslip._onchange_employee()
        attendence = self.payslip.worked_days_line_ids[0]
        attendence.write({
            'number_of_days': 32
        })
        with self.assertRaises(ValidationError):
            attendence._onchange_value_worked_days()
        attendence.write({
            'number_of_days': 31
        })
        attendence._onchange_value_worked_days()

        attendence.write({
            'number_of_days': 21
        })
        attendence._onchange_value_worked_days()

    def test_onchange_value_worked_days_other_contract(self):
        self.structure_type.write({
            'wage_type': "hourly"
        })
        contract_new = self.hr_contract.create({
            'name': "Test Contract 1",
            'structure_type_id': self.structure_type.id,
            'employee_id': self.employee_1.id,
            'date_start': date(2020, 2, 1),
            'wage_type': "hourly",
            'wage': 28000,
            'state': "open"
        })
        payslip_new = self.hr_payslip.create({
            'name': "Payroll Test 1",
            'date_from': date(2020, 2, 1),
            'date_to': date(2020, 2, 29),
            'employee_id': self.employee_1.id,
            'contract_id': contract_new.id
        })
        payslip_new._onchange_employee()
        attendence = payslip_new.worked_days_line_ids[0]
        attendence._onchange_value_worked_days()

    def test_employee_contract_start(self):
        self.structure_type.write({
            'wage_type': "monthly"
        })
        contract_new = self.hr_contract.create({
            'name': "Test Contract 1",
            'structure_type_id': self.structure_type.id,
            'employee_id': self.employee_1.id,
            'date_start': date(2020, 2, 10),
            'wage_type': "monthly",
            'wage': 28000,
            'state': "open"
        })
        payslip_new = self.hr_payslip.create({
            'name': "Payroll Test 1",
            'date_from': date(2020, 2, 1),
            'date_to': date(2020, 2, 29),
            'employee_id': self.employee_1.id,
            'contract_id': contract_new.id
        })

        # Inicio de contrato
        payslip_new._get_worked_day_lines()
        payslip_new._onchange_employee()

        attendence = payslip_new.worked_days_line_ids[0]
        attendence.write({
            'number_of_days': 30
        })
        attendence._onchange_value_worked_days()

        payslip_new = self.hr_payslip.create({
            'name': "Payroll Test 1",
            'date_from': date(2020, 3, 1),
            'date_to': date(2020, 3, 31),
            'employee_id': self.employee_1.id,
            'contract_id': contract_new.id
        })
        # Siguiente mes
        payslip_new._get_worked_day_lines()

        payslip_new._onchange_employee()
        attendence = payslip_new.worked_days_line_ids[0]
        attendence.write({
            'number_of_days': 30
        })
        attendence._onchange_value_worked_days()
