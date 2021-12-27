from datetime import datetime, timedelta
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo.fields import Date


class TestBitsHrPayrollNewsBatchBase(TransactionCase):

    def setUp(self):
        super(TestBitsHrPayrollNewsBatchBase, self).setUp()
        self.batch_ref = self.env['hr.payroll.news.batch']
        self.hr_employee = self.env['hr.employee']
        self.hr_contract = self.env['hr.contract']
        self.hr_payroll_structure_type = self.env['hr.payroll.structure.type']
        self.hr_payroll_structure = self.env['hr.payroll.structure']
        self.hr_salary_rule_category = self.env['hr.salary.rule.category']
        self.hr_salary_rule = self.env['hr.salary.rule']
        self.hr_payroll_news_stage = self.env['hr.payroll.news.stage']

        self.structure_type_01 = self.hr_payroll_structure_type.create({
            'name': "Empleado normal",
            'wage_type': "monthly"
        })

        self.structure_type = self.hr_payroll_structure_type.create({
            'name': "Type Desc Fijos",
            'wage_type': "monthly",
            'is_novelty': True
        })
        self.payroll_structure = self.hr_payroll_structure.create({
            'name': "Structure Desc Fijos",
            'type_id': self.structure_type.id
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

        self.contract = self.hr_contract.create({
            'name': "Contract Test",
            'date_start': datetime.now(),
            'date_end': datetime.now()+timedelta(days=365),
            'wage': 800000,
            'structure_type_id': self.structure_type_01.id
        })

        self.employee = self.hr_employee.create({
            'name': "Test Payroll News",
            'contract_id': self.contract.id,
            'identification_id': "75395146"
        })

        self.batch_new = self.batch_ref.create({
            'name': "Test Novelty",
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule.id,
            'employee_id': self.employee.id,
            'method_number': 12,
            'original_value': 1200000
        })

        self.batch_fixed = self.batch_ref.create({
            'name': 'Payroll batch',
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_code': 'TSTR',
            'identification_id': '75395146',
            'make_depreciation': False,
            'method_number': 1,
            'fixed_value': 26000,
            'first_depreciation_date': datetime.now()
        })

        self.batch_current = self.batch_ref.create({
            'name': 'Payroll batch',
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_code': 'TSTR',
            'identification_id': '75395146',
            'make_depreciation': True,
            'method_number': 3,
            'state': 'open',
            'fixed_value': 26000,
            'first_depreciation_date': datetime.now()
        })

        self.batch_last_month = self.batch_ref.create({
            'name': 'Payroll batch',
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_code': 'TSTR',
            'identification_id': '75395146',
            'make_depreciation': False,
            'method_number': 1,
            'state': 'open',
            'fixed_value': 26000,
            'first_depreciation_date': datetime.now()+timedelta(days=-30)
        })

        self.payrol_news_stage = self.hr_payroll_news_stage.create({
            'name': "Stage Won",
            'is_won': True
        })
