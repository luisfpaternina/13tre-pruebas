from odoo.exceptions import ValidationError, UserError
from .test_bits_hr_payroll_news import (TestBitsHrPayrollNews)


class TestHrEmployeePayrollNews(TestBitsHrPayrollNews):

    def setUp(self):
        super(TestHrEmployeePayrollNews, self).setUp()

    def test_compute_total(self):
        self.employee_payroll._compute_total()
        self.assertEqual(self.employee_payroll.total, 200)

    def test_get_amount_compute_rule(self):
        result = self.employee_payroll._get_amount_compute_rule()
        self.assertEqual(result, 3000)

        self.employee.write({
            'contract_id': False
        })
        result_0 = self.employee_payroll._get_amount_compute_rule()
        self.assertFalse(result_0)

        self.employee.write({
            'contract_id': self.contract.id
        })
        self.payroll_new.write({
            'salary_rule_id': False
        })
        self.employee_payroll._get_amount_compute_rule()
        result_1 = self.employee_payroll._get_amount_compute_rule()
        self.assertFalse(result_1)

        self.payroll_new.write({
            'salary_rule_id': self.salary_rule.id
        })
        self.salary_rule.write({
            'condition_select': "python",
            'condition_python': "result = 10>1"
        })
        result_2 = self.employee_payroll._get_amount_compute_rule()
        self.assertEqual(result_2, 3000)

    def test_onchange_employee_id(self):
        self.employee_payroll._onchange_employee_id()

        self.payroll_new.write({
            'salary_rule_id': False
        })
        with self.assertRaises(UserError):
            self.employee_payroll._onchange_employee_id()

    def test_onchange_employee_id_without_amount(self):
        self.salary_rule.write({
            'condition_select': "python",
            'condition_python': "10>1"
        })
        self.employee_payroll._onchange_employee_id()

    def test_get_base_local_dict(self):
        self.employee_payroll._get_base_local_dict()

    def test_check_float_items(self):
        self.employee_payroll._check_float_items()

        with self.assertRaises(ValidationError):
            self.hr_employee_payroll_news.create({
                'employee_id': self.employee.id,
                'quantity': 0,
                'amount': 100,
                'payroll_news_id': self.payroll_new.id
            })

    def test_hr_employee_payroll_news_create(self):
        with self.assertRaises(ValidationError):
            self.hr_employee_payroll_news.create({
                'identification_id': "951753456",
                'quantity': 2,
                'amount': 100,
                'payroll_news_id': self.payroll_new.id
            })

        self.hr_employee_payroll_news.create({
            'identification_id': "75395146",
            'quantity': 2,
            'amount': 100,
            'payroll_news_id': self.payroll_new.id
        })

    def test_get_number_of_days(self):
        self.salary_rule.write({
            'condition_holiday': 'none',
        })
        self.payroll_new.write({
            'request_date_from': '2020-04-17',
            'request_date_to': '2020-04-27',
        })

        self.employee_payroll._onchange_leave_dates()
        self.assertEqual(self.employee_payroll.quantity, 10)

    def test_get_number_of_days(self):
        data = {
            'employee_id': self.employee.id,
            'quantity': 10,
            'amount': 100,
            'payroll_news_id': self.payroll_new.id
        }
        record = self.hr_employee_payroll_news.new(data)

        res = record._onchange_leave_dates()
        self.assertEqual(res, None)

        self.salary_rule.write({
            'condition_holiday': 'none',
        })
        self.payroll_new.write({
            'request_date_from': '2020-04-13',
            'request_date_to': '2020-04-17',
        })

        # Get every day regardless of calendar.
        self.employee_payroll._onchange_leave_dates()
        self.assertEqual(self.employee_payroll.quantity, 5.0)

        self.salary_rule.write({
            'condition_holiday': 'work_days',
        })
        self.payroll_new.write({
            'condition_holiday': 'work_days',
        })

        # Get employee's worked days form calendar
        self.employee_payroll._onchange_leave_dates()
        self.assertEqual(self.employee_payroll.quantity, 5.0)

        self.payroll_new.write({
            'condition_holiday': 'non_work_days',
        })

        record = self.hr_employee_payroll_news.new(data)

        record._onchange_leave_dates()

        del(data['employee_id'])
        # Get the days worked from the global calendar.
        record = self.hr_employee_payroll_news.new(data)

        record._onchange_leave_dates()
        self.assertEqual(self.employee_payroll.quantity, 5.0)

    def test_create_line_from_user(self):
        record = self.hr_employee_payroll_news.create({
            'employee_id': self.employee.id,
            'quantity': 2,
            'amount': 100,
        })
        record.write({
            'payroll_news_id': self.payroll_new.id,
        })

        employee = self.hr_employee.create({
            'name': "Test Payroll News 2",
            'contract_id': self.contract.id,
            'identification_id': "175395146"
        })

        record.write({
            'employee_id': employee.id,
            'payroll_news_id': self.payroll_new.id,
            'quantity': 20,
            'amount': 55,
        })

        record.write({
            'payroll_news_id': False,
        })

        record.unlink()
