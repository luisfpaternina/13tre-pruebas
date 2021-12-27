# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPayrollHolidaysHistoryBase(TransactionCase):

    def setUp(self):
        super(TestPayrollHolidaysHistoryBase, self).setUp()
        self.HrWorkEntryType = self.env['hr.work.entry.type']
        self.HrPayrollHolidayLapse = self.env['hr.payroll.holiday.lapse']
        self.HrPayrollStructureType = self.env['hr.payroll.structure.type']
        self.HrPayrollStructure = self.env['hr.payroll.structure']
        self.HrPayrollNews = self.env['hr.payroll.news']

        self.ResourceCalendar = self.env['resource.calendar']
        self.ResourceCalendarLeaves = self.env['resource.calendar.leaves']
        self.HrPayslip = self.env['hr.payslip']
        self.HrEmployee = self.env['hr.employee']
        self.ResPartner = self.env['res.partner']
        self.HrSalaryRule = self.env['hr.salary.rule']
        self.HrJob = self.env['hr.job']
        self.HrContract = self.env['hr.contract']
        self.HrPayrollHolidaysHistory = self.env['hr.payroll.holidays.history']

        self.env['ir.config_parameter'].sudo().set_param(
            'hr_payroll.integrate_payroll_news', True)

        self.default_work_entry = self.HrWorkEntryType.create(
            {
                'name': 'My work entry',
                'code': 'MWE',
                'sequence': 25,
                'round_days': 'NO'
            }
        )

        self.HrSalaryRule.create({
            'name': 'VACACIONES EN DINERO',
            'code': 147,
            'category_id': self.env.ref(
                'bits_hr_payroll_news.category_novelty_01'
            ).id,
            'struct_id': self.env.ref(
                'bits_hr_payroll_news.structure_novelty_03'
            ).id,
            'sequence': 17,
            'constitutive': 'is_const',
            'condition_select': 'none',
            'amount_select': 'percentage',
            'condition_python': 1,
            'amount_percentage_base': 'contract.wage/30',
            'quantity': 1,
            'amount_percentage': 100.0000,
            'amount_fix': 6,
            'note': 'vacaciones en dinero',
            'affect_payslip': True,
            'affect_percentage_days': -1,
            'affect_worked_days': True,
            'constitutive_percentage': 100.0000,
            'non_constitutive_percentage': 100.0000,
            'condition_holiday': 'work_days'

        })

        self.salary_rule = self.HrSalaryRule.create({
            'name': "Test Rule 21",
            'code': "ICO",
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
        self.salary_rule_inco = self.HrSalaryRule.create({
            'name': "Test Rule 22",
            'code': "INCO",
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

        self.partner = self.ResPartner.create({
            'company_type': 'person',
            'name': 'Adrian Ayala Gonzalez'
        })

        self.job = self.HrJob.create({
            'name': 'Director administrativo y financiero'
        })

        self.salary_struct_normal = self.HrPayrollStructureType.create({
            'name': 'Empleado Normal',
            'wage_type': 'monthly',
            'default_schedule_pay': 'monthly',
            'default_work_entry_type_id': self.default_work_entry.id
        })

        self.salary_struct_intern = self.HrPayrollStructureType.create({
            'name': 'Aprendiz',
            'wage_type': 'monthly',
            'default_schedule_pay': 'monthly',
            'default_work_entry_type_id': self.default_work_entry.id
        })

        self.salary_struct_err = self.HrPayrollStructureType.create({
            'name': 'Otra',
            'wage_type': 'monthly',
            'default_schedule_pay': 'monthly',
            'default_work_entry_type_id': self.default_work_entry.id
        })

        self.calendar = self.ResourceCalendar.create(
            {
                'name': 'Standard 40 hours/week',
                'hours_per_day': 8.00,
                'tz': 'America/Bogota',
                'full_time_required_hours': 40.00,
                'work_time_rate': 100.00
            }
        )
        self.calendar_leaves = self.ResourceCalendarLeaves.create({
            'name': 'Festivo Colombia',
            'calendar_id': self.calendar.id,
            'date_from': datetime(2020, 6, 22, 0, 0, 0),
            'date_to': datetime(2020, 6, 22, 23, 59, 59)
        })

        self.contract = self.HrContract.create(
            {
                'name': 'Test contract',
                'structure_type_id': self.salary_struct_normal.id,
                'resource_calendar_id': self.calendar.id,
                'wage': 100000,
                'date_start': datetime.strptime(
                    '2014-01-31', '%Y-%m-%d'
                ),
                'state': 'open'
            }
        )

        self.contract_intern = self.HrContract.create(
            {
                'name': 'Test contract',
                'structure_type_id': self.salary_struct_normal.id,
                'resource_calendar_id': self.calendar.id,
                'wage': 100000,
                'date_start': datetime.strptime(
                    '2016-01-30', '%Y-%m-%d'
                ),
                'date_end': datetime.strptime(
                    '2016-08-31', '%Y-%m-%d'
                ),
                'state': 'open'
            }
        )

        self.contract_err = self.HrContract.create({
            'name': 'Test contract',
            'structure_type_id': self.salary_struct_err.id,
            'resource_calendar_id': self.calendar.id,
            'wage': 100000,
            'date_start': datetime.strptime(
                    '2018-11-20', '%Y-%m-%d'
            ),
            'state': 'open'
        })

        self.employee = self.HrEmployee.create(
            {
                'name': 'Adrian Ayala Gonzalez',
                'identification_id': '123456789',
                'job_id': self.job.id,
                'address_id': self.partner.id,
                'contract_id': self.contract.id,
                'resource_calendar_id': self.calendar.id
            }
        )
        self.employee2 = self.HrEmployee.create({
            'name': 'Carlos Vargas',
            'identification_id': '9876543210',
            'job_id': self.job.id
        })

        self.employee_err = self.HrEmployee.create({
            'name': 'Wilmer Vargas',
            'identification_id': '9873333210',
            'job_id': self.job.id,
            'contract_id': self.contract_err.id
        })

        self.employee_intern = self.HrEmployee.create(
            {
                'name': 'Freddy Ayala Gonzalez',
                'identification_id': '152356423',
                'job_id': self.job.id,
                'address_id': self.partner.id,
                'contract_id': self.contract_intern.id,
                'resource_calendar_id': self.calendar.id
            }
        )

        self.structure = self.HrPayrollStructure.create(
            {
                'name': 'Test structure',
                'type_id': self.salary_struct_normal.id,
            }
        )

        self.admin = self.env['res.users'].search([
            ('name', 'ilike', 'Admin')
        ], limit=1)

        self.salary_rule_extra = self.HrSalaryRule.search([
            ('code', '=', '60')
        ], limit=1)

        self.salary_rule_inco.struct_id.type_id.write({'is_novelty': True})

        self.HrPayrollNews.create({
            'name': 'Horas extra diurnas',
            'salary_rule_code': 'INCO',
            'payroll_structure_id': self.structure.id,
            'user_id': self.admin.id,
            'salary_rule_id': self.salary_rule_inco.id,
            'date_start': '2020-05-01',
            'date_end': '2020-05-01',
            'stage_id': 2,
            'employee_payroll_news_ids': [(
                0, 0, {
                    'employee_id': self.employee.id,
                    'quantity': 1,
                    'amount': 14583.3333
                }
            )]
        })

    def create_lapse(self):
        self.HrPayrollHolidayLapse._create_holiday_lapse()
        return self.HrPayrollHolidayLapse.search(
            [
                ('employee_id', '=', self.employee.id)
            ], limit=1
        )
