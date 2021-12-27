# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
from odoo.exceptions import ValidationError
from .common import (TestPayrollHolidaysHistoryBase)


class TestPayrollHolidayHistory(TestPayrollHolidaysHistoryBase):

    def setUp(self):
        super(TestPayrollHolidayHistory, self).setUp()

    def test_days_enjoyment_correct_1(self):
        holiday_lapse = self.create_lapse()
        history = self.HrPayrollHolidaysHistory.create(
            {
                'employee': self.employee.id,
                'holiday_lapse': holiday_lapse.id,
                'enjoyment_days': 7,
                'enjoyment_start_date': '2020-06-19',
                'enjoyment_end_date': '2020-06-27',
                'payment_date': datetime.strptime(
                    '2020-06-29', '%Y-%m-%d'
                ),
                'compensated_days': 5,
                'liquidated_period': 'month'
            }
        )
        history.create_holiday_news()
        history.approve_holiday_history()

    def test_repeat_holiday_history(self):
        holiday_lapse = self.create_lapse()
        history = self.HrPayrollHolidaysHistory.create(
            {
                'employee': self.employee.id,
                'holiday_lapse': holiday_lapse.id,
                'enjoyment_days': 7,
                'enjoyment_start_date': '2020-06-19',
                'enjoyment_end_date': '2020-06-27',
                'payment_date': datetime.strptime(
                    '2020-06-29', '%Y-%m-%d'
                ),
                'compensated_days': 0,
                'liquidated_period': 'month'
            }
        )
        history.create_holiday_news()
        history.approve_holiday_history()

        with self.assertRaises(ValidationError):
            history = self.HrPayrollHolidaysHistory.create(
                {
                    'employee': self.employee.id,
                    'holiday_lapse': holiday_lapse.id,
                    'enjoyment_days': 7,
                    'enjoyment_start_date': '2020-06-19',
                    'enjoyment_end_date': '2020-06-27',
                    'payment_date': datetime.strptime(
                        '2020-06-29', '%Y-%m-%d'
                    ),
                    'compensated_days': 0,
                    'liquidated_period': 'month'
                }
            )
            history.create_holiday_news()
            history.approve_holiday_history()

    def test_days_compensated_err(self):
        holiday_lapse = self.create_lapse()
        with self.assertRaises(ValidationError):
            history = self.HrPayrollHolidaysHistory.create(
                {
                    'employee': self.employee.id,
                    'holiday_lapse': holiday_lapse.id,
                    'enjoyment_days': 6,
                    'enjoyment_start_date': '2020-06-19',
                    'enjoyment_end_date': '2020-06-27',
                    'compensated_days': 9,
                    'payment_date': datetime.strptime(
                        '2020-06-29', '%Y-%m-%d'
                    ),
                    'liquidated_period': 'month'
                }
            )
            history.create_holiday_news()
            history.approve_holiday_history()

    def test_days_enjoyment_zero(self):
        holiday_lapse = self.create_lapse()

        with self.assertRaises(ValidationError):
            history = self.HrPayrollHolidaysHistory.create(
                {
                    'employee': self.employee.id,
                    'holiday_lapse': holiday_lapse.id,
                    'enjoyment_start_date': datetime.strftime(
                        datetime.now() - timedelta(10), '%Y-%m-%d'
                    ),
                    'enjoyment_days': 0,
                    'enjoyment_end_date': datetime.strftime(
                        datetime.now() - timedelta(10), '%Y-%m-%d'
                    ),
                    'payment_date': datetime.strftime(
                        datetime.now() - timedelta(5), '%Y-%m-%d'
                    ),
                    'liquidated_period': 'month'
                }
            )
            history.create_holiday_news()
            history.approve_holiday_history()

    def test_employee_whitout_contract(self):
        holiday_lapse = self.create_lapse()
        with self.assertRaises(ValidationError):
            history = self.HrPayrollHolidaysHistory.create(
                {
                    'employee': self.employee2.id,
                    'holiday_lapse': holiday_lapse.id,
                    'enjoyment_days': 7,
                    'enjoyment_start_date': '2020-06-19',
                    'enjoyment_end_date': '2020-06-27',
                    'compensated_days': 0,
                    'payment_date': datetime.strptime(
                        '2020-06-29', '%Y-%m-%d'
                    ),
                    'liquidated_period': 'month'
                }
            )
            history.create_holiday_news()
            history.approve_holiday_history()

    def test_compesated_days_error(self):
        holiday_lapse = self.create_lapse()
        with self.assertRaises(ValidationError):
            history = self.HrPayrollHolidaysHistory.create(
                {
                    'employee': self.employee.id,
                    'holiday_lapse': holiday_lapse.id,
                    'enjoyment_start_date': '2020-06-19',
                    'enjoyment_days': 2,
                    'enjoyment_end_date': '2020-06-20',
                    'compensated_days': 10,
                    'payment_date': datetime.strptime(
                        '2020-06-29', '%Y-%m-%d'
                    ),
                    'liquidated_period': 'month'
                }
            )

            history.create_holiday_news()
            history.approve_holiday_history()

    def test_days_enjoyment_correct(self):
        holiday_lapse = self.create_lapse()
        with self.assertRaises(ValidationError):
            history = self.HrPayrollHolidaysHistory.new({
                'employee': self.employee.id,
                'holiday_lapse': holiday_lapse.id,
                'enjoyment_start_date': '2020-06-19',
                'enjoyment_days': 5,
                'payment_date': datetime.strptime(
                    '2020-06-29', '%Y-%m-%d'
                ),
                'liquidated_period': 'month'
            })

            history.write({
                'enjoyment_start_date': datetime.now()
            })

            history._get_work_days_employee()
            history.create_holiday_news()
            history.approve_holiday_history()

    def test_days_enjoyment_sixteen(self):
        holiday_lapse = self.create_lapse()
        with self.assertRaises(ValidationError):
            history = self.HrPayrollHolidaysHistory.create(
                {
                    'employee': self.employee.id,
                    'holiday_lapse': holiday_lapse.id,
                    'enjoyment_start_date': datetime.strftime(
                        datetime.now() - timedelta(10), '%Y-%m-%d'
                    ),
                    'enjoyment_days': 16,
                    'enjoyment_end_date': datetime.strftime(
                        datetime.now() + timedelta(12), '%Y-%m-%d'
                    ),
                    'payment_date': datetime.strftime(
                        datetime.now() - timedelta(3), '%Y-%m-%d'
                    ),
                    'liquidated_period': 'month'
                }
            )
            history.create_holiday_news()
            history.approve_holiday_history()

    def test_history_sum_days_sixteen(self):
        holiday_lapse = self.create_lapse()
        history1 = self.HrPayrollHolidaysHistory.create(
            {
                'employee': self.employee.id,
                'holiday_lapse': holiday_lapse.id,
                'enjoyment_start_date': datetime.strftime(
                    datetime.now() - timedelta(5), '%Y-%m-%d'
                ),
                'enjoyment_days': 6,
                'enjoyment_end_date': datetime.strftime(
                    datetime.now() + timedelta(3), '%Y-%m-%d'
                ),
                'compensated_days': 0,
                'payment_date': datetime.strftime(
                    datetime.now() - timedelta(2), '%Y-%m-%d'
                ),
                'liquidated_period': 'month'
            }
        )
        history1.create_holiday_news()
        history1.approve_holiday_history()
        with self.assertRaises(ValidationError):
            history2 = self.HrPayrollHolidaysHistory.create(
                {
                    'employee': self.employee.id,
                    'holiday_lapse': holiday_lapse.id,
                    'enjoyment_start_date': datetime.strftime(
                        datetime.now() - timedelta(40), '%Y-%m-%d'
                    ),
                    'enjoyment_days': 11,
                    'enjoyment_end_date': datetime.strftime(
                        datetime.now() - timedelta(27), '%Y-%m-%d'
                    ),
                    'payment_date': datetime.strftime(
                        datetime.now() - timedelta(23), '%Y-%m-%d'
                    ),
                    'compensated_days': 0,
                    'liquidated_period': 'month'
                }
            )
            history2.create_holiday_news()
            history2.approve_holiday_history()

    def test_month_next(self):
        holiday_lapse = self.create_lapse()
        history = self.HrPayrollHolidaysHistory.create(
            {
                'employee': self.employee.id,
                'holiday_lapse': holiday_lapse.id,
                'enjoyment_days': 6,
                'enjoyment_start_date': '2020-06-29',
                'enjoyment_end_date': '2020-07-1',
                'payment_date': datetime.strptime(
                    '2020-06-29', '%Y-%m-%d'
                ),
                'compensated_days': 0,
                'liquidated_period': 'month'
            }
        )
        history.create_holiday_news()
        history.approve_holiday_history()

    def test_history_states(self):
        holiday_lapse = self.create_lapse()
        with self.assertRaises(ValidationError):
            history = self.HrPayrollHolidaysHistory.create(
                {
                    'employee': self.employee.id,
                    'holiday_lapse': holiday_lapse.id,
                    'enjoyment_days': 6,
                    'enjoyment_start_date': '2020-06-29',
                    'enjoyment_end_date': '2020-07-1',
                    'payment_date': datetime.strptime(
                        '2020-06-29', '%Y-%m-%d'
                    ),
                    'compensated_days': 0,
                    'liquidated_period': 'month'
                }
            )
            history.create_holiday_news()
            history.approve_holiday_history()
            history.cancel_holiday_history()
            history.create_holiday_news()
            novelties = history.payroll_news_ids
            novelties[1].stage_id.is_won = True
            history.approve_holiday_history()
            history.cancel_holiday_history()
            history.approve_holiday_history()

    def test_different_months_one_days(self):
        holiday_lapse = self.create_lapse()
        history = self.HrPayrollHolidaysHistory.create(
            {
                'employee': self.employee.id,
                'holiday_lapse': holiday_lapse.id,
                'enjoyment_days': 6,
                'enjoyment_start_date': '2020-02-20',
                'enjoyment_end_date': '2020-03-2',
                'payment_date': datetime.strptime(
                    '2020-06-29', '%Y-%m-%d'
                ),
                'compensated_days': 0,
                'liquidated_period': 'month'
            }
        )
        history.create_holiday_news()
        history.approve_holiday_history()

    def test_different_months_two_days(self):
        holiday_lapse = self.create_lapse()
        history = self.HrPayrollHolidaysHistory.create(
            {
                'employee': self.employee.id,
                'holiday_lapse': holiday_lapse.id,
                'enjoyment_days': 6,
                'enjoyment_start_date': '2021-02-20',
                'enjoyment_end_date': '2021-03-2',
                'payment_date': datetime.strptime(
                    '2020-06-29', '%Y-%m-%d'
                ),
                'compensated_days': 0,
                'liquidated_period': 'month'
            }
        )
        history.validate_holiday(date(2020, 2, 2))
        history.create_holiday_news()
        history.approve_holiday_history()
