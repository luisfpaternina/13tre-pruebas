from datetime import datetime, timedelta
from odoo.fields import Date
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase
from dateutil.relativedelta import relativedelta


class TestPayrollProvisionsReport(TransactionCase):

    def setUp(self):
        super(TestPayrollProvisionsReport, self).setUp()
        self.hr_employee = self.env['hr.employee']
        self.hr_contract = self.env['hr.contract']
        self.hr_payslip = self.env['hr.payslip']
        self.hr_social_security = self.env['social.security']
        self.hr_payroll_new = self.env['hr.payroll.news']
        self.hr_salary_rule = self.env['hr.salary.rule']
        self.hr_salary_rule_category = self.env['hr.salary.rule.category']
        self.ResourceCalendar = self.env['resource.calendar']
        self.ProvisionsReport = self.env['payroll.provisions.report']
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

        self.payroll_structure = self.env.ref(
            'bits_hr_payroll_news.structure_novelty_02'
        )

        self.salary_rule_category = self.hr_salary_rule_category.create({
            'name': "Salary Category Test",
            'code': "SCT"
        })

        self.salary_rule = self.hr_salary_rule.create({
            'name': "ITEM PROVISIONES",
            'code': "001",
            'sequence': 100,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1.0
        })

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

        self.contract2 = self.hr_contract.create({
            "name": "Employee Test Contract2",
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

        self.employee2 = self.hr_employee.create({
            "name": "Employee Test 2",
            "identification_id": "1005483250",
            "contract_id": self.contract2.id,
            "resource_calendar_id": self.calendar.id
        })

        self.payroll_new = self.hr_payroll_new.create({
            "name": "Test Novelty",
            "payroll_structure_id": self.payroll_structure.id,
            "salary_rule_id": self.salary_rule.id,
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

        self.payroll_new2 = self.hr_payroll_new.create({
            "name": "Test Novelty2",
            "payroll_structure_id": self.payroll_structure.id,
            "salary_rule_id": self.salary_rule.id,
            "stage_id": self.payrol_news_stage.id,
            "employee_payroll_news_ids": [
                [
                    0,
                    0,
                    {
                        "payroll_news_id": False,
                        "quantity": 1,
                        "employee_id": self.employee2.id,
                        "amount": 20
                    }
                ]
            ]
        })

        payslip = self.hr_payslip.create({
            "name": "Payroll Test",
            "employee_id":  self.employee.id,
            "contract_id": self.contract.id,
            'date_from': datetime.now().replace(day=1),
            'date_to': datetime.now()+relativedelta(months=+1),
            'state': 'done',
            "line_ids": [(0, 0, {
                'sequence': self.salary_rule.sequence,
                'code': self.salary_rule.code,
                'name': self.salary_rule.name,
                'salary_rule_id': self.salary_rule.id,
                'amount': 20,
                'quantity': 1,
                'slip_id': self.id,
                'rate': self.salary_rule.amount_percentage or 100,
            })]
        })

        payslip2 = self.hr_payslip.create({
            "name": "Payroll Test 2",
            "employee_id":  self.employee.id,
            "contract_id": self.contract.id,
            'date_from': datetime.now().replace(
                day=1)+relativedelta(months=+1),
            'date_to': datetime.now()+relativedelta(months=+2),
            'state': 'done',
            "line_ids": [(0, 0, {
                'sequence': self.salary_rule.sequence,
                'code': self.salary_rule.code,
                'name': self.salary_rule.name,
                'salary_rule_id': self.salary_rule.id,
                'amount': 20,
                'quantity': 1,
                'slip_id': self.id,
                'rate': self.salary_rule.amount_percentage or 100,
            })]
        })

        payslip3 = self.hr_payslip.new({
            "name": "Payroll Test 2",
            "employee_id":  self.employee2.id,
            "contract_id": self.contract2.id,
            'date_from': datetime.now().replace(day=1),
            'date_to': datetime.now()+relativedelta(months=+1),
            'state': 'done',
            "line_ids": [(0, 0, {
                'sequence': self.salary_rule.sequence,
                'code': self.salary_rule.code,
                'name': self.salary_rule.name,
                'salary_rule_id': self.salary_rule.id,
                'amount': 20,
                'quantity': 1,
                'slip_id': self.id,
                'rate': self.salary_rule.amount_percentage or 100,
            })]
        })

    def test_export_report_all_employees(self):
        record = self.ProvisionsReport.new({
            'date_start': datetime.now()-relativedelta(months=+2),
            'date_end': datetime.now()+relativedelta(months=+2),
            'all_employees': True,
        })

        config = self.env['res.config.settings'].create({})
        config.salary_provision_rule = self.salary_rule.ids
        config.overtime_provision_rule = self.salary_rule.ids
        config.adjustment_provision_rule = self.salary_rule.ids
        config.closing_adjustment_provision_rule = self.salary_rule.ids
        config.bonus_provision_rule = self.salary_rule.ids
        config.provision_rule = self.salary_rule.ids
        config.vacations_provision_rule = [self.env.ref(
            'bits_hr_payroll_news.hr_payroll_structure_employee_02').id]
        config.execute()

        record.generate_excel_report()

    def test_export_report_one_employees(self):
        record = self.ProvisionsReport.new({
            'date_start': datetime.now()-relativedelta(months=+2),
            'date_end': datetime.now()+relativedelta(months=+1),
            'all_employees': False,
            'employees': self.employee.id
        })

        config = self.env['res.config.settings'].create({})
        config.salary_provision_rule = self.salary_rule.ids
        config.overtime_provision_rule = self.salary_rule.ids
        config.adjustment_provision_rule = self.salary_rule.ids
        config.closing_adjustment_provision_rule = self.salary_rule.ids
        config.bonus_provision_rule = self.salary_rule.ids
        config.provision_rule = self.salary_rule.ids
        config.vacations_provision_rule = [self.env.ref(
            'bits_hr_payroll_news.hr_payroll_structure_employee_02').id]
        config.execute()

        record.generate_excel_report()
