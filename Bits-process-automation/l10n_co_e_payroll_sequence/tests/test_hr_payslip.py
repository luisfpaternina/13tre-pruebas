from datetime import datetime, date
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestCoEPayrollSequence(TransactionCase):

    def setUp(self):
        super(TestCoEPayrollSequence, self).setUp()
        self.hr_payslip = self.env['hr.payslip']
        self.hr_payroll_structure = self.env['hr.payroll.structure']
        self.hr_payroll_structure_type = self.env['hr.payroll.structure.type']
        self.hr_work_entry_type = self.env['hr.work.entry.type']
        self.ir_sequence = self.env['ir.sequence']
        self.hr_employee = self.env['hr.employee']

        self.hr_employee_1 = self.hr_employee.create({
            'name': "Empleado 1",
        })

        self.hr_work_entry_type_1 = self.hr_work_entry_type.create({
            'name': "Name work entry 1",
            'code': "CODE 01",
            'round_days': 'NO'
        })

        self.hr_work_entry_type_2 = self.hr_work_entry_type.create({
            'name': "Name work entry 2",
            'code': "CODE 02",
            'round_days': 'FULL'
        })

        self.hr_payroll_structure_type_1 = (self.
                                            hr_payroll_structure_type).create({
                                                'name': "Structure type 1",
                                                'wage_type': 'hourly',
                                                'default_work_entry_type_id':
                                                (self.hr_work_entry_type_1.id)
                                                })

        self.hr_payroll_structure_type_2 = (self.
                                            hr_payroll_structure_type).create({
                                                'name': "Structure type 2",
                                                'wage_type': 'monthly',
                                                'default_work_entry_type_id':
                                                (self.hr_work_entry_type_2.id)
                                            })

        self.ir_sequence_1 = self.ir_sequence.create({
            'name': "Test sequence_1",
            'padding': 1,
            'number_increment': 1,
            'prefix': "PRE",
            'suffix': "SU",
            'number_next': 1
        })

        self.ir_sequence_2 = self.ir_sequence.create({
            'name': "Test sequence_2",
            'padding': 2,
            'number_increment': 1,
            'prefix': "PRE",
            'suffix': "SU",
            'number_next': 2
        })

        self.hr_payroll_structure_1 = self.hr_payroll_structure.create({
            'name': "Test Payroll structure 1",
            'sequence_id': self.ir_sequence_1.id,
            'type_id': self.hr_payroll_structure_type_1.id,
        })

        self.hr_payroll_structure_2 = self.hr_payroll_structure.create({
            'name': "Test Payroll structure 2",
            'sequence_id': self.ir_sequence_2.id,
            'type_id': self.hr_payroll_structure_type_2.id,
        })

        self.hr_payroll_structure_3 = self.hr_payroll_structure.create({
            'name': "Test Payroll structure 2",
            'sequence_id': False,
            'type_id': self.hr_payroll_structure_type_2.id,
        })

        self.hr_payslip_1 = self.hr_payslip.create({
            'name': "Test payslip 1",
            'struct_id': self.hr_payroll_structure_1.id,
            'employee_id': self.hr_employee_1.id,
        })

        self.hr_payslip_2 = self.hr_payslip.create({
            'name': "Test payslip 2",
            'struct_id': self.hr_payroll_structure_2.id,
            'employee_id': self.hr_employee_1.id,
        })

        self.hr_payslip_3 = self.hr_payslip.create({
            'name': "Test payslip 3",
            'struct_id': self.hr_payroll_structure_3.id,
            'employee_id': self.hr_employee_1.id,
        })

    def test_action_payslip_done_with_structure(self):
        self.hr_payslip_1.action_payslip_done()

    def test_action_payslip_done_with_structure_without_code(self):
        self.hr_payslip_2.action_payslip_done()

    def test_action_payslip_done_without_structure_3(self):
        self.hr_payslip_3.action_payslip_done()
