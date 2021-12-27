# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo.fields import Date
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestPayrollPaycheck(TransactionCase):

    def setUp(self):
        super(TestPayrollPaycheck, self).setUp()
        self.wizard_ref = self.env['send.email.paycheck']
        self.hr_employee = self.env['hr.employee']
        self.hr_payroll_structure = self.env['hr.payroll.structure']
        self.hr_payroll_structure_type = self.env['hr.payroll.structure.type']
        self.hr_contract = self.env['hr.contract']
        self.hr_payslip = self.env['hr.payslip']
        self.HrResPartner = self.env['res.partner']

        self.contact = self.HrResPartner.create({
            'name': 'partner name',
        })

        self.structure_type = self.hr_payroll_structure_type.create({
            'name': "Test Type",
            'wage_type': "monthly"
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
        })
        self.employee = self.hr_employee.create({
            'name': "Test Payroll News",
            'contract_id': self.contract.id,
            'identification_id': "75395146",
            'address_home_id': self.contact.id
        })

        self.payslip = self.hr_payslip.create({
            'name': "Payroll Test",
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'struct_id': self.payroll_structure.id,
            'date_from': datetime.now().strftime('%Y-%m-01'),
            'date_to': str(datetime.now() + relativedelta(
                months=+1, day=1, days=-1))[:10]
        })

        self.contact = self.HrResPartner.create({
            'name': 'partner name 2',
        })
        self.employee2 = self.hr_employee.create({
            'name': "Employee 2",
            'contract_id': self.contract.id,
            'identification_id': "125395146",
            'address_home_id': self.contact.id

        })
        self.payslip2 = self.hr_payslip.create({
            'name': "Payslip 2",
            'employee_id': self.employee2.id,
            'contract_id': self.contract.id,
            'struct_id': self.payroll_structure.id,
            'date_from': datetime.now(),
            'date_to': datetime.now()+timedelta(days=365)
        })
