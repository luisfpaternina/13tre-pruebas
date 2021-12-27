# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo.fields import Date
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPayrollSettlement(TransactionCase):

    def setUp(self):
        super(TestPayrollSettlement, self).setUp()
        self.wizard_ref = self.env['send.email.paycheck']
        self.hr_employee = self.env['hr.employee']
        self.hr_payroll_structure = self.env['hr.payroll.structure']
        self.hr_payroll_structure_type = self.env['hr.payroll.structure.type']
        self.hr_contract = self.env['hr.contract']
        self.hr_payslip = self.env['hr.payslip']
        self.HrResPartner = self.env['res.partner']
        self.settlement_ref = self.env['settlement.history']
        self.batch_ref = self.env['hr.payroll.news.batch']
        self.hr_salary_rule_category = self.env['hr.salary.rule.category']
        self.hr_salary_rule = self.env['hr.salary.rule']
        self.social_security = self.env['social.security']

        self.social_security_1 = self.social_security.create({
            'code': '00001',
            'name': 'Test Name',
        })

        self.contact = self.HrResPartner.create({
            'name': 'partner name',
        })

        self.stage_approved = self.env.ref(
            'bits_hr_payroll_news.stage_payroll_news2')

        self.structure_type = self.hr_payroll_structure_type.create({
            'name': "Test Type",
            'wage_type': "monthly",
            'is_novelty': True
        })

        self.payroll_structure = self.hr_payroll_structure.create({
            'name': "Structure Test",
            'type_id': self.structure_type.id
        })

        self.contract = self.hr_contract.create({
            'name': "Contract Test",
            'date_start': datetime.now(),
            'date_end': datetime.now()+timedelta(days=365),
            'wage': 800000,
            'structure_type_id': self.structure_type.id,
            'risk_class': self.social_security_1.id,
        })
        self.employee = self.hr_employee.create({
            'name': "Test Payroll News",
            'names': "Test Payroll News",
            'surnames': 'APELLIDO1 APELLIDO2',
            'known_as': 'SuperCode',
            'document_type': '13',
            'contract_id': self.contract.id,
            'identification_id': "75395146",
            'address_home_id': self.contact.id
        })

        self.payslip = self.hr_payslip.create({
            'name': "Payroll Test",
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'struct_id': self.payroll_structure.id,
            'state': 'verify',
            'date_from': datetime.now().strftime('%Y-%m-01'),
            'date_to': str(datetime.now() + relativedelta(
                months=+1, day=1, days=-1))[:10]
        })

        self.contact = self.HrResPartner.create({
            'name': 'partner name 2',
        })
        self.employee2 = self.hr_employee.create({
            'name': "Employee 2",
            'names': "Test Payroll News",
            'surnames': 'APELLIDO1 APELLIDO2',
            'known_as': 'SuperCode',
            'document_type': '13',
            'identification_id': "125395146",
            'address_home_id': self.contact.id

        })
        self.payslip2 = self.hr_payslip.create({
            'name': "Payslip 2",
            'employee_id': self.employee2.id,
            'contract_id': self.contract.id,
            'struct_id': self.payroll_structure.id,
            'date_from': datetime.now(),
            'date_to': datetime.now()+timedelta(days=30)
        })

        self.termination = self.ref(
            'hr_payroll_settlement.reason_dsjc_nor')

        self.settlement = self.settlement_ref.create({
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'date_payment': datetime.now(),
            'reason_for_termination': self.termination,
            'compensation': False,
        })

        self.settlement2 = self.settlement_ref.create({
            'employee_id': self.employee2.id,
            'contract_id': self.contract.id,
            'date_payment': datetime.now(),
            'reason_for_termination': self.termination,
            'compensation': False,
        })

        self.salary_rule_category = self.hr_salary_rule_category.create({
            'name': "Salary Category Desc Fijos",
            'code': "SCT"
        })
        self.salary_rule = self.hr_salary_rule.create({
            'name': "Descuento fijo davivienda",
            'code': "TSTR",
            'sequence': 100,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1.0,
            'constitutive': "is_const"
        })

        self.salary_rule_data = self.hr_salary_rule.create({
            'name': "LICENCIA NO REMUNERADA - SUELDO",
            'code': "3120",
            'sequence': 100,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "percentage",
            'amount_percentage': -100,
            'condition_python': 1,
            'amount_fix': 8,
            'appears_on_payslip': True,
            'not_remunerate': True,
            'affect_payslip': False,
            'affect_percentage_days': -1,
            'affect_worked_days': True,
            'constitutive_percentage': 100,
            'non_constitutive_percentage': 100,
            'quantity': 1.0,
        })

        self.salary_rule_extra = self.hr_salary_rule.search([
            ('code', '=', 'TSTR')
        ], limit=1)
        self.payroll_news = self.env['hr.payroll.news'].create({
            'name': 'Horas extra diurnas',
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule_extra.id,
            'salary_rule_code': self.salary_rule_extra.code,
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

        self.batch_new = self.batch_ref.create({
            'name': "Test Novelty",
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule.id,
            'employee_id': self.employee.id,
            'method_number': 12,
            'original_value': 1200000
        })

        self.batch_new2 = self.batch_ref.create({
            'name': "Test Novelty",
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule.id,
            'employee_id': self.employee.id,
            'method_number': 6,
            'original_value': 500000
        })

        self.holiday_lapse = self.env['hr.payroll.holiday.lapse'].create({
            'name': ' ',
            'begin_date': datetime.now(),
            'employee_id': self.employee.id,
            'end_date': datetime.now(),
            'type_vacation': 'normal',
            'state': '1',
            'pending_days': 15
        })

        self.history = self.env['hr.payroll.holidays.history'].create({
            'employee': self.employee.id,
            'holiday_lapse': self.holiday_lapse.id,
            'enjoyment_days': 6,
            'enjoyment_start_date': '2020-06-17',
            'enjoyment_end_date': '2020-06-23',
            'payment_date': datetime.strptime(
                '2020-06-29', '%Y-%m-%d'
            ),
            'compensated_days': 5,
            'liquidated_period': 'month'
        })

        self.salary_rule_extra1 = self.hr_salary_rule.search([
            ('code', '=', 'TSTR')
        ], limit=1)

        self.payroll_news1 = self.env['hr.payroll.news'].create({
            'name': 'Horas extra diurnas',
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule_extra1.id,
            'salary_rule_code': self.salary_rule_extra1.code,
            'date_start': '2021-01-09',
            'date_end': '2021-01-09',
            'stage_id': 2,
            'employee_payroll_news_ids': [(
                0, 0, {
                    'employee_id': self.employee.id,
                    'quantity': 1,
                    'amount': 14583.3333
                }
            )]
        })
