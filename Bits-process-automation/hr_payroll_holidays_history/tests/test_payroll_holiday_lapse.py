# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
from .common import (TestPayrollHolidaysHistoryBase)


class TestPayrollHolidayLapse(TestPayrollHolidaysHistoryBase):

    def setUp(self):
        super(TestPayrollHolidayLapse, self).setUp()

    def test_create_holiday_lapse(self):
        self.HrPayrollHolidayLapse.create(
            {
                'name': ' ',
                'begin_date': datetime.strftime(
                    datetime.now() - timedelta(367), '%Y-%m-%d'
                ),
                'end_date': datetime.strftime(
                    datetime.now() - timedelta(2), '%Y-%m-%d'
                ),
                'employee_id': self.employee.id,
                'type_vacation': 'normal',
                'state': '1',
            }
        )
        self.create_lapse()

    def test_contract_whitout_struct(self):
        self.HrPayrollHolidayLapse.create(
            {
                'name': ' ',
                'begin_date': datetime.strftime(
                    datetime.now() - timedelta(367), '%Y-%m-%d'
                ),
                'employee_id': self.employee_err.id,
                'end_date': datetime.strftime(
                    datetime.now() - timedelta(2), '%Y-%m-%d'
                ),
                'type_vacation': 'normal',
                'state': '1',
            }
        )

    def test_create_second_lapse(self):
        self.HrPayrollHolidayLapse.create(
            {
                'name': ' ',
                'begin_date': datetime.strftime(
                    datetime.now() - timedelta(367), '%Y-%m-%d'
                ),
                'employee_id': self.employee_intern.id,
                'end_date': datetime.strftime(
                    datetime.now() - timedelta(2), '%Y-%m-%d'
                ),
                'type_vacation': 'normal',
                'state': '1',
            }
        )

        self.contract_intern.write({
            'structure_type_id': self.salary_struct_intern.id
        })

        self.HrPayrollHolidayLapse._create_holiday_lapse()

    def test_create_lapse_without_name(self):
        self.HrPayrollHolidayLapse.create({
            'begin_date': datetime.strftime(
                datetime.now() - timedelta(367), '%Y-%m-%d'
            ),
            'employee_id': self.employee.id,
            'end_date': datetime.strftime(
                datetime.now() - timedelta(2), '%Y-%m-%d'
            ),
            'type_vacation': 'normal',
            'state': '1',
        })

    def test_create_lapse_no_current(self):
        self.HrPayrollHolidayLapse.create(
            {
                'name': ' ',
                'begin_date': datetime.strftime(
                    datetime.now() - timedelta(367), '%Y-%m-%d'
                ),
                'employee_id': self.employee.id,
                'end_date': datetime.strftime(
                    datetime.now() - timedelta(2), '%Y-%m-%d'
                ),
                'type_vacation': 'normal',
                'state': '2',
            }
        )
        self.create_lapse()

    def test_create_development_span(self):
        self.HrPayrollHolidayLapse.create(
            {
                'name': ' ',
                'begin_date': datetime.strftime(
                    datetime.now() - timedelta(165), '%Y-%m-%d'
                ),
                'employee_id': self.employee.id,
                'end_date': datetime.strftime(
                    datetime.now() + timedelta(200), '%Y-%m-%d'
                ),
                'type_vacation': 'normal',
                'state': '1',
            }
        )
        self.create_lapse()

    def test_correct_number_holiday_days(self):
        self.HrPayrollHolidayLapse.create(
            {
                'name': ' ',
                'begin_date': datetime.strftime(
                    datetime.now() - timedelta(165), '%Y-%m-%d'
                ),
                'employee_id': self.employee.id,
                'end_date': datetime.strftime(
                    datetime.now() + timedelta(200), '%Y-%m-%d'
                ),
                'type_vacation': 'normal',
                'state': '1',
            }
        )
        self.create_lapse()
        self.create_lapse()

    def create_struct_custom_and_update(self, name):
        struct = self.env[
            'hr.payroll.structure.type'
        ].create(
            {
                'name': name,
                'wage_type': 'monthly',
                'default_schedule_pay': 'monthly',
                'default_work_entry_type_id': self.default_work_entry.id
            }
        )
        self.contract.update(
            {
                'structure_type_id': struct.id
            }
        )

    def _create_lapse_and_prepare(self):
        lapse = self.HrPayrollHolidayLapse.create(
            {
                'name': ' ',
                'begin_date': datetime.strftime(
                    datetime.now() - timedelta(165), '%Y-%m-%d'
                ),
                'employee_id': self.employee.id,
                'end_date': datetime.strftime(
                    datetime.now() + timedelta(200), '%Y-%m-%d'
                ),
                'type_vacation': 'normal',
                'state': '1',
            }
        )
        lapse._prepare_holiday_lapse(self.employee, lapse.begin_date)

    def test_integral_holiday(self):
        self.create_struct_custom_and_update('integral')
        self._create_lapse_and_prepare()

    def test_normal_holiday(self):
        self.create_struct_custom_and_update('normal')
        self._create_lapse_and_prepare()

    def test_electiva_holiday(self):
        self.HrPayrollHolidayLapse._create_holiday_lapse()
        self.create_struct_custom_and_update('electiva')
        self.HrPayrollHolidayLapse._create_holiday_lapse()
