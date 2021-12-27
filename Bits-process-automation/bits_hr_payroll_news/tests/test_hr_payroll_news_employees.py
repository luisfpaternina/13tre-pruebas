from odoo.exceptions import ValidationError, UserError
from .test_bits_hr_payroll_news import (TestBitsHrPayrollNews)


class TestHrEmployeePayrollNews(TestBitsHrPayrollNews):

    def setUp(self):
        super(TestHrEmployeePayrollNews, self).setUp()

    def test_add_employees_action(self):
        wizard = self.env['hr.payroll.news.wizard'].create({
            'name': "Test Novelty",
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule.id,
            'quantity': 1,
            'amount': 400,
            'employee_ids': self.employee,
        })

        wizard.with_context({
            'default_parent_model': 'hr.employee.payroll.news',
            'active_id': self.payroll_new.id
        }).add_employees_action()
        wizard.add_employees_action()

    def test_add_novelty_employee_action(self):
        wizard1 = self.env['hr.payroll.news.wizard'].new({})
        wizard1._compute_total()
        wizard1._default_payroll_structure_id()
        wizard = self.env['hr.payroll.news.wizard'].new({
            'name': "Test Novelty",
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule.id,
            'employee_ids': self.employee
        })

        wizard.with_context({
            'default_parent_model': 'hr.employee.payroll.news',
            'default_model': 'hr.payroll.news',
            'active_id': self.payroll_new.id,
            'employee_ids': [self.employee.id],
        }).add_novelty_employee_action()

        wizard2 = self.env['hr.payroll.news.wizard'].new({
            'name': "Test Novelty",
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule.id,
            'employee_ids': self.employee
        })

        wizard2.add_novelty_employee_action()

        wizard2.with_context({
            'default_model': 'hr.payroll.news',
            # 'default_parent_model': 'hr.employee.payroll.news',
            'employee_ids': [self.employee.id],
        }).add_novelty_employee_action()

        wizard2.with_context({
            'default_model': 'hr.payroll.news',
            'employee_ids': [12312312]
        }).add_novelty_employee_action()
