# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from odoo.fields import Date
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestCommonSeverancePay(TransactionCase):

    def setUp(self):
        super(TestCommonSeverancePay, self).setUp()

        self.HrContract = self.env['hr.contract']
        self.HrEmployee = self.env['hr.employee']

        self.HrPayrollStructureType = self.env['hr.payroll.structure.type']
        self.HrPayrollStructure = self.env['hr.payroll.structure']
        self.HrSalaryRuleCategory = self.env['hr.salary.rule.category']
        self.HrSalaryRule = self.env['hr.salary.rule']
        self.HrPayrollNewsStage = self.env['hr.payroll.news.stage']
        self.HrPayrollNews = self.env['hr.payroll.news']
        self.HrPayslip = self.env['hr.payslip']

        self.salary_structure = self.env.ref(
            'bits_hr_payroll_news.hr_payroll_structure_type_employee_01')

        self.contract = self.HrContract.create({
            'name': 'Contract Test',
            'rate': 4.3500,
            'date_start': datetime.now().replace(day=1, month=1),
            'structure_type_id': self.salary_structure.id,
            'wage': 3600000.00,
            'contract_history_ids': [(0, 0, {
                '_type': 'wage',
                'date': datetime.now().replace(day=4, month=9).date(),
                'adjusment_date': datetime.now().replace(
                    day=4, month=9).date(),
                'last_salary': 3400000.00,
                'amount': 3600000.00
            })]
        })

        self.contract_test = self.HrContract.create({
            'name': 'Contract Test',
            'rate': 4.3500,
            'date_start': datetime.now().replace(day=1, month=1),
            'date_end': datetime.now().replace(day=31, month=3),
            'structure_type_id': self.salary_structure.id,
            'wage': 3600000.00
        })

        self.contract_date_end = self.HrContract.create({
            'name': 'Contract with date end',
            'rate': 4.3500,
            'date_start': datetime.now().replace(day=30, month=11, year=2019),
            'date_end': datetime.now().replace(day=31, month=5),
            'structure_type_id': self.salary_structure.id,
            'wage': 4000000.00,
            'contract_history_ids': [(0, 0, {
                '_type': 'wage',
                'date': datetime.now().replace(day=1, month=1).date(),
                'adjusment_date': datetime.now().replace(
                    day=1, month=1).date(),
                'last_salary': 3400000.00,
                'amount': 3600000.00
            }), (0, 0, {
                '_type': 'wage',
                'date': datetime.now().replace(day=1, month=4).date(),
                'adjusment_date': datetime.now().replace(
                    day=1, month=4).date(),
                'last_salary': 3600000.00,
                'amount': 4000000.00
            })]
        })

        self.employee = self.HrEmployee.create({
            'name': 'Test Employee',
            'contract_id': self.contract.id,
            'identification_id': '20365210232'
        })

        self.fixed_employee = self.HrEmployee.create({
            'name': 'Test Employee Fixed',
            'contract_id': self.contract_date_end.id,
            'identification_id': '20365210232'
        })

        self.structure_type = self.HrPayrollStructureType.create({
            'name': 'Structure type test',
            'wage_type': 'monthly',
            'is_novelty': True
        })

        self.payroll_structure = self.env.ref(
            'bits_hr_payroll_news.hr_payroll_structure_employee_01')

        self.work_entry_type = self.env.ref(
            'hr_work_entry.work_entry_type_attendance')

        self.salary_rule_category = self.env.ref(
            'hr_payroll_severance_pay.category_social_benefits_01')

        self.salary_rule_compute_holidays = self.HrSalaryRule.create({
            'name': 'Salary Rule Test',
            'code': 'SRT',
            'category_id': self.salary_rule_category.id,
            'sequence': 185,
            'struct_id': self.payroll_structure.id,
            'active': True,
            'condition_select': 'none',
            'amount_select': 'percentage',
            'amount_percentage_base': """
                provisions.compute_holidays_pay('WORK100',codes=[]
                ,from_date=payslip.date_from,to_date=payslip.date_to)
            """,
            'quantity': '1',
            'amount_percentage': 100.0000
        })

        self.salary_rule_severance_pay = self.HrSalaryRule.create({
            'name': 'Salary Rule Test',
            'code': 'SSP',
            'category_id': self.salary_rule_category.id,
            'sequence': 185,
            'struct_id': self.payroll_structure.id,
            'active': True,
            'condition_select': 'none',
            'amount_select': 'percentage',
            'amount_percentage_base': """
                provisions.compute_severance_pay(
                'WORK100',codes=[], period=0)""",
            'quantity': '1',
            'amount_percentage': 100.0000
        })

        self.salary_rule_proincre = self.HrSalaryRule.create({
            'name': 'Salary Rule Test',
            'code': 'PROINCRETEST',
            'category_id': self.salary_rule_category.id,
            'sequence': 185,
            'struct_id': self.payroll_structure.id,
            'active': True,
            'condition_select': 'none',
            'amount_select': 'percentage',
            'amount_percentage_base': """
                provisions.compute_provisions_severance_incremental(
                    ['BASIC', '120'],codes=[],percentage=12,
                from_date=payslip.date_from,to_date=payslip.date_to)""",
            'quantity': '1',
            'amount_percentage': 100.0000
        })

        self.salary_rule_provision = self.HrSalaryRule.create({
            'name': 'Salary Rule Test',
            'code': 'PROVESION',
            'category_id': self.salary_rule_category.id,
            'sequence': 185,
            'struct_id': self.payroll_structure.id,
            'active': True,
            'condition_select': 'none',
            'amount_select': 'percentage',
            'amount_percentage_base': """
                provisions.compute_provisions(['BASIC'],
                codes=['60','65','70','75','321'],
                from_date=payslip.date_from)""",
            'quantity': '1',
            'amount_percentage': 100.0000
        })

        self.september_payslip = self.HrPayslip.create({
            'name': 'Payroll Test',
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'struct_id': self.payroll_structure.id,
            'date_from': datetime.now().replace(day=1, month=9).date(),
            'date_to': datetime.now().replace(day=30, month=9).date(),
            'worked_days_line_ids': [(0, 0, {
                'work_entry_type_id': self.work_entry_type.id,
                'number_of_days': 30,
                'amount': 3400000.00
            })]
        })

        self.jan_payslip = self.HrPayslip.create({
            'name': 'Payroll Test',
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'struct_id': self.payroll_structure.id,
            'date_from': datetime.now().replace(day=1, month=1).date(),
            'date_to': datetime.now().replace(day=31, month=1).date(),
            'worked_days_line_ids': [(0, 0, {
                'work_entry_type_id': self.work_entry_type.id,
                'number_of_days': 30,
                'amount': 3400000.00
            })]
        })

        self.december_payslip = self.HrPayslip.create({
            'name': 'Payroll Test',
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'struct_id': self.payroll_structure.id,
            'date_from': datetime.now().replace(day=1, month=12).date(),
            'date_to': datetime.now().replace(day=31, month=12).date(),
            'worked_days_line_ids': [(0, 0, {
                'work_entry_type_id': self.work_entry_type.id,
                'number_of_days': 30,
                'amount': 3400000.00
            })]
        })

        self.march_payslip = self.HrPayslip.create({
            'name': 'Payroll Test',
            'employee_id': self.employee.id,
            'contract_id': self.contract_test.id,
            'struct_id': self.payroll_structure.id,
            'date_from': datetime.now().replace(day=1, month=3).date(),
            'date_to': datetime.now().replace(day=31, month=3).date(),
            'worked_days_line_ids': [(0, 0, {
                'work_entry_type_id': self.work_entry_type.id,
                'number_of_days': 30,
                'amount': 3400000.00
            })]
        })

        self.fixed_payslip = self.HrPayslip.create({
            'name': 'Payroll Test',
            'employee_id': self.fixed_employee.id,
            'contract_id': self.contract_date_end.id,
            'struct_id': self.payroll_structure.id,
            'date_from': datetime.now().replace(day=1, month=5).date(),
            'date_to': datetime.now().replace(day=31, month=5).date(),
            'worked_days_line_ids': [(0, 0, {
                'work_entry_type_id': self.work_entry_type.id,
                'number_of_days': 30,
                'amount': 3400000.00
            })]
        })

        self.stage_id = self.HrPayrollNewsStage.search([
            ('is_approved', '=', True)
        ], limit=1)

        self.salary_rule_he = self.HrSalaryRule.search([
            ('code', '=', '75')
        ], limit=1)

        self.HrPayrollNews.create({
            'name': 'Horas Extras',
            'date_start': datetime.now().replace(day=1, month=9),
            'date_end': datetime.now().replace(day=30, month=9),
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule_he.id,
            'stage_id': self.stage_id.id,
            'employee_payroll_news_ids': [(0, 0, {
                'employee_id': self.employee.id,
                'quantity': 1,
                'amount': 60000
            })]
        })
