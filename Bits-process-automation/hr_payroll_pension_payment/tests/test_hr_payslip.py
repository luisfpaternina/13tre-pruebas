from datetime import datetime, timedelta, date
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError


class TestHrPayslip(TransactionCase):

    def setUp(self):
        super(TestHrPayslip, self).setUp()
        self.hr_employee = self.env['hr.employee']
        self.hr_salary_rule = self.env['hr.salary.rule']
        self.hr_contract = self.env['hr.contract']
        self.hr_payslip = self.env['hr.payslip']
        self.config_settings = self.env['res.config.settings']
        self.hr_work_entry_type = self.env['hr.work.entry.type']
        self.hr_payroll_structure_type = self.env['hr.payroll.structure.type']

        self.salary_rule_0 = self.hr_salary_rule.search(
            [('code', '=', '3020')], limit=1)

        self.employee = self.hr_employee.create({
            'name': "Juan Perez",
            'pensions_contrib': False
        })

        self.employee_2 = self.hr_employee.create({
            'name': "Juan Perez 2",
            'pensions_contrib': True
        })

        self.work_entry_type = self.env.ref(
            'hr_work_entry.work_entry_type_attendance')

        self.salary_structure = self.env.ref(
            'bits_hr_payroll_news.hr_payroll_structure_employee_01')

        self.salary_structure_type = self.env.ref(
            'bits_hr_payroll_news.hr_payroll_structure_type_employee_01')

        self.contract = self.hr_contract.create({
            'name': "Test Contract",
            'structure_type_id': self.salary_structure_type.id,
            'employee_id': self.employee.id,
            'date_start': date(2020, 1, 1),
            'wage_type': "monthly",
            'wage': 5800000,
            'state': 'open'
        })

        self.payslip = self.hr_payslip.create({
            'name': "Payroll Test",
            'date_from': date(2020, 1, 1),
            'date_to': date(2020, 1, 31),
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'struct_id': self.salary_structure.id,
            'worked_days_line_ids': [(0, 0, {
                'work_entry_type_id': self.work_entry_type.id,
                'number_of_days': 30,
                'amount': 5800000
            })]
        })

        self.payslip_2 = self.hr_payslip.create({
            'name': "Payroll Test",
            'date_from': date(2020, 1, 1),
            'date_to': date(2020, 1, 31),
            'employee_id': self.employee_2.id,
            'contract_id': self.contract.id,
            'struct_id': self.salary_structure.id,
            'worked_days_line_ids': [(0, 0, {
                'work_entry_type_id': self.work_entry_type.id,
                'number_of_days': 30,
                'amount': 5800000
            })]
        })

    def test_compute_sheet(self):
        self.payslip.compute_sheet()

    def test_compute_sheet_2(self):
        self.payslip_2.compute_sheet()

    def test_rule(self):
        rule_contrib_pension = self.env.ref(
            '__export__.hr_salary_rule_bits_08'
        )

        config = self.env['res.config.settings'].create({})
        config.rule_contrib_pension = [rule_contrib_pension.id]
        config.execute()
