from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError
from .common import (TestPayrollHolidaysHistoryBase)


class TestPayslip(TestPayrollHolidaysHistoryBase):

    def setUp(self):
        super(TestPayslip, self).setUp()

        self.holiday_structure = self.env.ref(
            'hr_payroll_holidays_history.structure_holidays')

        self.salary_structure = self.env.ref(
            'bits_hr_payroll_news.hr_payroll_structure_type_employee_01')

        self.work_entry_type = self.env.ref(
            'hr_work_entry.work_entry_type_attendance')

        self.stage_approved = self.env['hr.payroll.news.stage'].search([
            ('is_approved', '=', True)
        ], limit=1)

        self.employee_worked_days = self.HrEmployee.create({
            'name': 'Pedro Suarez',
            'identification_id': '65236524',
        })

        self.contract_worked = self.HrContract.create({
            'name': "Test Contract",
            'structure_type_id': self.salary_struct_normal.id,
            'employee_id': self.employee_worked_days.id,
            'date_start': date(2020, 1, 1),
            'wage_type': "monthly",
            'risk_class': '1',
            'rate': 2.222,
            'wage': 2800000,
            'state': "open"
        })

        self.lapse = self.HrPayrollHolidayLapse.create({
            'name': 'Period Test',
            'begin_date': datetime.strftime(
                datetime.now() - timedelta(367), '%Y-%m-%d'
            ),
            'employee_id': self.employee_worked_days.id,
            'end_date': datetime.strftime(
                datetime.now() - timedelta(2), '%Y-%m-%d'
            ),
            'type_vacation': 'normal',
            'state': '1',
        })

        self.holiday_payslip = self.HrPayslip.create({
            'name': 'test payroll',
            'date_from': date(2020, 6, 1),
            'date_to': date(2020, 6, 30),
            'employee_id': self.employee_worked_days.id,
            'contract_id': self.contract_worked.id,
            'struct_id': self.holiday_structure.id,
            'general_state': 'sent',
            'worked_days_line_ids': [(0, 0, {
                'work_entry_type_id': self.work_entry_type.id,
                'number_of_days': 30,
                'amount': 3400000.00
            })]
        })

        self.holiday_payslip_normal = self.HrPayslip.create({
            'name': 'test payroll normal',
            'date_from': date(2020, 6, 1),
            'date_to': date(2020, 6, 30),
            'employee_id': self.employee_worked_days.id,
            'contract_id': self.contract_worked.id,
            'struct_id': self.salary_structure.id,
            'general_state': 'sent',
            'worked_days_line_ids': [(0, 0, {
                'work_entry_type_id': self.work_entry_type.id,
                'number_of_days': 30,
                'amount': 3400000.00
            })]
        })

    def setting_struct_holiday(self):
        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.holiday_structure_ids',
            [self.holiday_structure.id])

    def test_holiday_payslip(self):
        self.setting_struct_holiday()
        history = self.HrPayrollHolidaysHistory.create(
            {
                'employee': self.employee_worked_days.id,
                'holiday_lapse': self.lapse.id,
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

        for novelty in history.payroll_news_ids:
            novelty.write({
                'stage_id': self.stage_approved.id
            })

        self.holiday_payslip.compute_sheet()
        self.holiday_payslip.approve_payroll()

    def test_holiday_payslip_normal(self):
        self.holiday_payslip_normal.compute_sheet()
        self.holiday_payslip_normal.approve_payroll()

    def test_holiday_ibc_variation(self):
        self.setting_struct_holiday()
        history = self.HrPayrollHolidaysHistory.create(
            {
                'employee': self.employee_worked_days.id,
                'holiday_lapse': self.lapse.id,
                'enjoyment_days': 6,
                'enjoyment_start_date': '2020-06-25',
                'enjoyment_end_date': '2020-06-27',
                'payment_date': datetime.strptime(
                    '2020-06-29', '%Y-%m-%d'
                ),
                'compensated_days': 0,
                'liquidated_period': 'month',
                'global_state': 'approval'
            }
        )

        history.create_holiday_news()
        history.approve_holiday_history()

        for novelty in history.payroll_news_ids:
            novelty.write({
                'stage_id': self.stage_approved.id
            })

        self.salary_rule_ibc = self.HrSalaryRule.create({
            'name': "Test Rule 22",
            'code': "IBC",
            'category_id': self.env.ref(
                'bits_hr_payroll_news.category_novelty_01'
            ).id,
            'struct_id': self.env.ref(
                'hr_payroll_holidays_history.structure_holidays'
            ).id,
            'sequence': 100,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1.0,
            'constitutive': "is_const"
        })

        self.holiday_payslip.compute_sheet()
        self.holiday_payslip.approve_payroll()

    def test_holiday_ibc_variation_err(self):
        self.setting_struct_holiday()
        history = self.HrPayrollHolidaysHistory.create(
            {
                'employee': self.employee_worked_days.id,
                'holiday_lapse': self.lapse.id,
                'enjoyment_days': 6,
                'enjoyment_start_date': '2020-06-25',
                'enjoyment_end_date': '2020-06-27',
                'payment_date': datetime.strptime(
                    '2020-06-29', '%Y-%m-%d'
                ),
                'compensated_days': 0,
                'liquidated_period': 'month',
                'global_state': 'approval'
            }
        )

        history.create_holiday_news()
        history.approve_holiday_history()

        for novelty in history.payroll_news_ids:
            novelty.write({
                'stage_id': self.stage_approved.id
            })

        self.salary_rule_ibc = self.HrSalaryRule.create({
            'name': "Test Rule 22",
            'code': "IBC",
            'category_id': self.env.ref(
                'bits_hr_payroll_news.category_novelty_01'
            ).id,
            'struct_id': self.env.ref(
                'hr_payroll_holidays_history.structure_holidays'
            ).id,
            'sequence': 100,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1.0,
            'constitutive': "is_const",
            "apply_other_rules": "3010,3020,3023",
        })

        self.holiday_payslip.compute_sheet()
        self.holiday_payslip.approve_payroll()

    def test_holiday_ibc_variation_amount(self):
        self.setting_struct_holiday()
        history = self.HrPayrollHolidaysHistory.create(
            {
                'employee': self.employee_worked_days.id,
                'holiday_lapse': self.lapse.id,
                'enjoyment_days': 6,
                'enjoyment_start_date': '2020-06-25',
                'enjoyment_end_date': '2020-06-27',
                'payment_date': datetime.strptime(
                    '2020-06-29', '%Y-%m-%d'
                ),
                'compensated_days': 0,
                'liquidated_period': 'month',
                'global_state': 'approval'
            }
        )

        history.create_holiday_news()
        history.approve_holiday_history()

        for novelty in history.payroll_news_ids:
            novelty.write({
                'stage_id': self.stage_approved.id
            })

        self.salary_rule_ibc = self.HrSalaryRule.create({
            'name': "Test Rule 22",
            'code': "IBC",
            'category_id': self.env.ref(
                'bits_hr_payroll_news.category_novelty_01'
            ).id,
            'struct_id': self.env.ref(
                'hr_payroll_holidays_history.structure_holidays'
            ).id,
            'sequence': 100,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1.0,
            'constitutive': "is_const",
            "apply_other_rules": "3010,3020,3023",
            "apply_in": "amount"
        })

        self.holiday_payslip.compute_sheet()
        self.holiday_payslip.approve_payroll()

    def test_holiday_ibc_variation_total(self):
        self.setting_struct_holiday()
        history = self.HrPayrollHolidaysHistory.create(
            {
                'employee': self.employee_worked_days.id,
                'holiday_lapse': self.lapse.id,
                'enjoyment_days': 6,
                'enjoyment_start_date': '2020-06-25',
                'enjoyment_end_date': '2020-06-27',
                'payment_date': datetime.strptime(
                    '2020-06-29', '%Y-%m-%d'
                ),
                'compensated_days': 0,
                'liquidated_period': 'month',
                'global_state': 'approval'
            }
        )

        history.create_holiday_news()
        history.approve_holiday_history()

        for novelty in history.payroll_news_ids:
            novelty.write({
                'stage_id': self.stage_approved.id
            })

        self.salary_rule_ibc = self.HrSalaryRule.create({
            'name': "Test Rule 22",
            'code': "IBC",
            'category_id': self.env.ref(
                'bits_hr_payroll_news.category_novelty_01'
            ).id,
            'struct_id': self.env.ref(
                'hr_payroll_holidays_history.structure_holidays'
            ).id,
            'sequence': 100,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1.0,
            'constitutive': "is_const",
            "apply_other_rules": "3010,3020,3023",
            "apply_in": "total"
        })

        self.holiday_payslip.compute_sheet()
        self.holiday_payslip.approve_payroll()

    def test_holiday_ibc_variation_with_old_period(self):
        self.setting_struct_holiday()

        self.holiday_payslip_old = self.HrPayslip.create({
            'name': 'test payroll',
            'date_from': date(2020, 5, 1),
            'date_to': date(2020, 5, 30),
            'employee_id': self.employee_worked_days.id,
            'contract_id': self.contract_worked.id,
            'struct_id': self.holiday_structure.id,
            'general_state': 'sent',
            'worked_days_line_ids': [(0, 0, {
                'work_entry_type_id': self.work_entry_type.id,
                'number_of_days': 30,
                'amount': 3400000.00
            })]
        })
        self.holiday_payslip_old.compute_sheet()
        self.holiday_payslip_old.approve_payroll()

        history = self.HrPayrollHolidaysHistory.create(
            {
                'employee': self.employee_worked_days.id,
                'holiday_lapse': self.lapse.id,
                'enjoyment_days': 6,
                'enjoyment_start_date': '2020-06-25',
                'enjoyment_end_date': '2020-06-27',
                'payment_date': datetime.strptime(
                    '2020-06-29', '%Y-%m-%d'
                ),
                'compensated_days': 0,
                'liquidated_period': 'month',
                'global_state': 'approval'
            }
        )

        history.create_holiday_news()
        history.approve_holiday_history()

        for novelty in history.payroll_news_ids:
            novelty.write({
                'stage_id': self.stage_approved.id
            })

        self.salary_rule_ibc = self.HrSalaryRule.create({
            'name': "Test Rule 22",
            'code': "IBC",
            'category_id': self.env.ref(
                'bits_hr_payroll_news.category_novelty_01'
            ).id,
            'struct_id': self.env.ref(
                'hr_payroll_holidays_history.structure_holidays'
            ).id,
            'sequence': 100,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1.0,
            'constitutive': "is_const",
            "apply_other_rules": "3010,3020,3023",
            "apply_in": "total"
        })

        self.holiday_payslip.compute_sheet()
        self.holiday_payslip.approve_payroll()
