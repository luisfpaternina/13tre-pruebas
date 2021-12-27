from datetime import datetime, timedelta
from odoo.fields import Date
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPayrollHolidays(TransactionCase):

    def setUp(self):
        super(TestPayrollHolidays, self).setUp()
        self.hr_employee = self.env['hr.employee']
        self.hr_contract = self.env['hr.contract']
        self.hr_payslip = self.env['hr.payslip']
        self.hr_payroll_holiday_lapse = self.env['hr.payroll.holiday.lapse']
        self.hr_payroll_holiday_history = (
            self.env['hr.payroll.holidays.history']
        )
        self.hr_social_security = self.env['social.security']
        self.ResourceCalendar = self.env['resource.calendar']
        self.hr_payroll_new = self.env['hr.payroll.news']
        self.hr_salary_rule = self.env['hr.salary.rule']
        self.hr_payroll_news_stage = self.env['hr.payroll.news.stage']
        self.payrol_news_stage = self.hr_payroll_news_stage.create({
            'name': "Stage Test"
        })

        self.social_secrity = self.hr_social_security.create({
            "code": "6",
            "name": "Risk Class VI",
            "entity_type": "risk_class"
        })

        self.salary_structure = self.env.ref(
            'bits_hr_payroll_news.hr_payroll_structure_type_employee_01')

        self.salary_rule_1 = self.hr_salary_rule.search([])
        self.salary_rule_2 = ""

        for record in self.salary_rule_1:
            if record.code == "145":
                self.salary_rule_2 = record

        self.payroll_structure = self.env.ref(
            'bits_hr_payroll_news.structure_novelty_02'
        )

        self.calendar = self.ResourceCalendar.create({
            'name': 'Standard 40 hours/week',
            'hours_per_day': 8.00,
            'tz': 'America/Bogota',
            'full_time_required_hours': 40.00,
            'work_time_rate': 100.00
        })

        self.contract = self.hr_contract.create({
            "name": "Employee Test Contract",
            "risk_class": self.social_secrity.id,
            "structure_type_id": self.salary_structure.id,
            "type_contract": "non-fixed",
            "date_start": datetime(2010, 2, 20),
            "wage": 4500000,
            "resource_calendar_id": self.calendar.id,
            "state": "open"
        })

        self.employee = self.hr_employee.create({
            "name": "Employee Test",
            "identification_id": "1005483249",
            "contract_id": self.contract.id,
            "resource_calendar_id": self.calendar.id
        })

        self.payroll_new = self.hr_payroll_new.create({
            "name": "Test Novelty",
            "payroll_structure_id": self.payroll_structure.id,
            "salary_rule_id": self.salary_rule_2.id,
            "stage_id": self.payrol_news_stage.id,
            "employee_payroll_news_ids": [
                [
                    0,
                    0,
                    {
                        "payroll_news_id": False,
                        "quantity": 1,
                        "employee_id": self.employee.id,
                        "amount": 20
                    }
                ]
            ]
        })

        self.payslip = self.hr_payslip.create({
            "name": "Payroll Test",
            "employee_id":  self.employee.id,
            "contract_id": self.contract.id,
            'date_from': datetime.now(),
            'date_to': datetime.now()+timedelta(days=365)
        })

    def create_lapse(self):
        self.hr_payroll_holiday_lapse._create_holiday_lapse()
        print("\n")
        print(self.hr_payroll_holiday_lapse.search([]))
        return self.hr_payroll_holiday_lapse.search(
            [
                ('employee_id', '=', self.employee.id)
            ], limit=1
        )
