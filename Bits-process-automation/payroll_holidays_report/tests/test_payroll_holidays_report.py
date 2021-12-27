from datetime import datetime, timedelta
from odoo.addons.payroll_holidays_report.tests.common \
    import TestPayrollHolidays


class TestPayrollHolidaysReport(TestPayrollHolidays):

    def setUp(self):
        super(TestPayrollHolidaysReport, self).setUp()

    def test_validation_compute_period_strat_date(self):

        hr_holidays_history = self.hr_payroll_holiday_history.create({
            "employee": self.employee.id,
            "holiday_lapse": self.create_lapse().id,
            "enjoyment_start_date": "2020-10-12",
            "enjoyment_end_date": "2020-10-20",
            "payment_date": "2020-9-28",
            "liquidated_period": "month",
            "enjoyment_days": 8.0,
            "compensated_days": 4.0
        })

        payslip = self.hr_payslip.create({
            "name": "Payroll Test",
            "employee_id":  self.employee.id,
            "contract_id": self.contract.id,
            'date_from': datetime.now(),
            'date_to': datetime.now()+timedelta(days=365),
            "line_ids": [(0, 0, {
                'sequence': self.salary_rule_2.sequence,
                'code': self.salary_rule_2.code,
                'name': self.salary_rule_2.name,
                'salary_rule_id': self.salary_rule_2.id,
                'amount': 20,
                'quantity': 1,
                'slip_id': self.id,
                'payroll_news_id': [self.payroll_new.id],
                'rate': self.salary_rule_2.amount_percentage or 100,
            })]
        })

        self.payslip._compute_date_now()
        self.payslip._compute_period_start_date()
        self.payslip._compute_period_end_date()
        self.payslip._compute_enjoyment_start_date()
        self.payslip._compute_enjoyment_end_date()

    def test_validation_date(self):
        date = datetime(2020, 10, 10)
        self.payslip.date_format(date)
