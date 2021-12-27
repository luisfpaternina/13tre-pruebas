from datetime import datetime, timedelta, date
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestHrPayslipRun(TransactionCase):

    def setUp(self):
        super(TestHrPayslipRun, self).setUp()
        self.HrPayslipRun = self.env['hr.payslip.run']
        self.HRPayslipEmployees = self.env['hr.payslip.employees']
        self.HRPayrollStructureType = self.env['hr.payroll.structure.type']
        self.HRPayrollStructure = self.env['hr.payroll.structure']
        self.HrWorkEntryType = self.env['hr.work.entry.type']

        self.payslip_run = self.HrPayslipRun.create({
            'name': "Test Payslip Run",
            'date_start': date(2020, 5, 1),
            'date_end': date(2020, 5, 31)
        })
        self.entry_type = self.HrWorkEntryType.create({
            'name': "Test",
            'code': 'TST100'
        })
        self.structure_type = self.HRPayrollStructureType.create({
            'name': "TST Struct Type",
            'default_work_entry_type_id': self.entry_type.id
        })
        self.structure = self.HRPayrollStructure.create({
            'name': "TST Struct",
            'type_id': self.structure_type.id
        })

    def test_onchange_structure(self):
        payslip_employee = self.HRPayslipEmployees.new({
            'structure_id': False
        })
        payslip_employee._onchange_structure()

        payslip_employee_1 = self.HRPayslipEmployees.new({
            'structure_id': self.structure.id
        })
        payslip_employee_1._onchange_structure()
