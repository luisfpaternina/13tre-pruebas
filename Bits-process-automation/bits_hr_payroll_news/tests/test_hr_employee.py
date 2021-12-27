from odoo.exceptions import ValidationError
from .test_bits_hr_payroll_news import (TestBitsHrPayrollNews)


class TestHrEmployee(TestBitsHrPayrollNews):

    def setUp(self):
        super(TestHrEmployee, self).setUp()

    def test_compute_payroll_news_count(self):
        self.employee._compute_payroll_news_count()
        # Add line create payroll news
        # Add line to edit payroll news
        self.assertEqual(self.employee.payroll_news_count, 2)

    def test_add_novelty_action(self):
        self.employee.add_novelty_action()

    def test_payroll_news_view(self):
        self.employee.payroll_news_view()
