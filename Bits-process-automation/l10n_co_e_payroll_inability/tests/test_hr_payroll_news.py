# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import logging


class TestEPayroll(TransactionCase):

    def setUp(self):
        super(TestEPayroll, self).setUp()

        self.hr_employee = self.env['hr.employee']
        self.hr_salary_rule = self.env['hr.salary.rule']
        self.hr_payroll_structure = self.env['hr.payroll.structure']
        self.hr_payroll_structure_type = self.env['hr.payroll.structure.type']
        self.hr_salary_rule_category = self.env['hr.salary.rule.category']
        self.hr_inability = self.env['hr.inability']
        self.hr_payroll_news = self.env['hr.payroll.news']

        self.salary_rule_category = self.hr_salary_rule_category.create({
            'name': "Salary Category Test",
            'code': "SCT"
        })

        self.hr_employee_1 = self.hr_employee.create({
            'name': "Empleado 1",
        })

        self.structure_type = self.hr_payroll_structure_type.create({
            'name': "Test Type",
            'wage_type': "monthly",
            "is_novelty": True
        })

        self.payroll_structure_1 = self.hr_payroll_structure.create({
            'name': "Structure Test 1",
            'type_id': self.structure_type.id,
        })

        self.salary_rule_66 = self.hr_salary_rule.create({
            'name': "TEST RANDON",
            'code': "001",
            'sequence': 100,
            'struct_id': self.payroll_structure_1.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1.0,
        })

        self.hr_inability_1 = self.hr_inability.create({
            'name': "Común",
            'code': 1,
        })

        self.hr_payroll_news_1 = self.hr_payroll_news.create({
            'name': "Hr Payroll News test 01",
            'salary_rule_code': "001",
            'inability_id': self.hr_inability_1.id,
            'employee_payroll_news_ids': [
                (
                    0,
                    0,
                    {
                        'employee_id': self.hr_employee_1.id,
                        'quantity': 16,
                        'amount': 35000,
                    }
                )
            ],
            'salary_rule_id': self.salary_rule_66.id,
        })

    def test_clear_domain_inability_id(self):
        self.hr_payroll_news_1._clear_domain_inability_id()
