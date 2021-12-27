from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import date
from datetime import datetime, timedelta
import logging
import re


class TestHrEmployee(TransactionCase):

    def setUp(self):
        self.hr_employee = self.env['hr.employee']
        self.hr_contract = self.env['hr.contract']
        self.hr_payroll_structure = self.env['hr.payroll.structure']
        self.hr_payroll_structure_type = self.env['hr.payroll.structure.type']
        self.res_config = self.env['res.config.settings']
        self.conf_para = self.env['ir.config_parameter']
        self.structure_type_integral = self.hr_payroll_structure_type.create({
        super(TestHrEmployee, self).setUp()
        self.hr_employee = self.env['hr.employee']
        self.hr_contract = self.env['hr.contract']
        self.hr_payroll_structure_type = self.env['hr.payroll.structure.type']
        self.structure_type = self.hr_payroll_structure_type.create({
            'name': "Empleado integral",
            'wage_type': "monthly"
        })
        self.structure_type_normal = self.hr_payroll_structure_type.create({
            'name': "Empleado normal",
            'wage_type': "monthly"
        })

        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.integral_salary_structure_ids',
            [self.structure_type_integral.id])
        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.integral_structure_type_payroll_ids',
            [self.structure_type.id]
        )
        self.contract = self.hr_contract.create({
            'name': "Contract Test",
            'date_start': datetime.now(),
            'date_end': datetime.now()+timedelta(days=365),
            'wage': 3150000,
            'structure_type_id': self.structure_type_integral.id,
            'high_risk_pension': True,
        })
            'structure_type_id': self.structure_type.id,
            'high_risk_pension': True,
        })
        self.employee = self.hr_employee.create({
            'name': "Test Payroll News",
            'contract_id': self.contract.id,
        })

    def test_check_high_risk_pension(self):
        self.employee._check_high_risk_pension()

    def test_check_integral_salary(self):
        # SIN Tipo de SALARIO CONFIGURADO
        self.employee._check_integral_salary()
        self.assertFalse(self.employee.integral_salary)

        config = self.env['res.config.settings'].create({})
        config.integral_structure_type_payroll_ids\
            = [self.structure_type_integral.id]
        config.execute()

        # con tipo SALARIO CONFIGURADO
        self.employee._check_integral_salary()
        self.assertTrue(self.employee.integral_salary)

        # Cambio de contrato de integral a normal
        self.contract.structure_type_id = self.structure_type_normal
        self.employee._check_integral_salary()
        self.assertFalse(self.employee.integral_salary)
        self.employee._check_integral_salary()

    def test_check_integral_salary_without_contract(self):
        employee2 = self.hr_employee.create({
            'name': "Test Payroll News",
        })
        employee2._check_integral_salary()

    def test_check_get_values(self):
        config = self.env['res.config.settings'].create({})
        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.integral_structure_type_payroll_ids',
            [self.structure_type.id]
        )
        config.execute()
