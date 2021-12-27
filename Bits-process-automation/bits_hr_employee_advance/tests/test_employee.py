from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import date, datetime, timedelta
import re


class TestHrEmployee(TransactionCase):

    def setUp(self):
        super(TestHrEmployee, self).setUp()
        self.HrEmployee = self.env['hr.employee']

    # Compute age whit birthday date
    def test_compute_age_with_birthday(self):
        new_employee = self.HrEmployee.create({
            'name': 'Abigail Peterson',
            'names': 'Abigail',
            'surnames': 'Peterson',
            'document_type': '13',
            'identification_id': '1234567895',
            'known_as': 'Abigail',
            'birthday': date(1993, 11, 20),
            'spouse_birthdate': date(1993, 11, 20)
        })

        new_employee._compute_age()
        self.assertEqual(new_employee.age, 26)

    # Compute age whitout birthday date
    def test_compute_age_without_birthday(self):
        new_employee = self.HrEmployee.create({
            'name': 'Abigail Peterson',
            'names': 'Abigail',
            'surnames': 'Peterson',
            'document_type': '13',
            'identification_id': '1234567895',
            'known_as': 'Abigail'
        })

        new_employee._compute_age()
        new_employee._validate_email()
        new_employee._compute_time_at_bits()

    # test compute time at bits whit begin date
    def test_compute_time_at_bits_whith_begindate(self):
        new_employee = self.HrEmployee.create({
            'name': 'Abigail Peterson',
            'names': 'Abigail',
            'surnames': 'Peterson',
            'document_type': '13',
            'identification_id': '1234567895',
            'known_as': 'Abigail',
            'begin_date': date(2016, 11, 20)
        })

        self.assertEqual(new_employee.time_at_bits, 3)

    # test validate email format
    def test_validate_email(self):
        new_employee = self.HrEmployee.create({
            'name': 'Abigail Peterson',
            'names': 'Abigail',
            'surnames': 'Peterson',
            'document_type': '13',
            'identification_id': '1234567895',
            'known_as': 'Abigail',
            'email_emergency_contact': 'abigail@gmail.com'
        })

        self.assertEqual(new_employee.email_emergency_contact,
                         'abigail@gmail.com')

    # test validate email whit format error
    def test_invalid_email(self):

        with self.assertRaises(ValidationError):
            new_employee = self.HrEmployee.create({
                'name': 'Abigail Peterson',
                'names': 'Abigail',
                'surnames': 'Peterson',
                'document_type': '13',
                'identification_id': '1234567895',
                'known_as': 'Abigail',
                'email_emergency_contact': 'abigailgmail.com'
            })

    def test_validation_cc_alphanumeric(self):

        with self.assertRaises(ValidationError):
            self.HrEmployee.create({
                'name': 'Abigail Peterson',
                'names': 'Abigail',
                'surnames': 'Peterson',
                'known_as': 'Abigail',
                'document_type': '13',
                'identification_id': '52a8s2ds'
            })

    def test_validation_ti_length(self):
        with self.assertRaises(ValidationError):
            self.HrEmployee.create({
                'name': 'Abigail Peterson',
                'names': 'Abigail',
                'surnames': 'Peterson',
                'known_as': 'Abigail',
                'document_type': '12',
                'identification_id': '631236521452123'
            })

    def test_validation_passport_length(self):
        with self.assertRaises(ValidationError):
            self.HrEmployee.create({
                'name': 'Abigail Peterson',
                'names': 'Abigail',
                'surnames': 'Peterson',
                'known_as': 'Abigail',
                'document_type': '41',
                'identification_id': '6a2s'
            })

    def test_validation_passport_alphanumeric(self):
        with self.assertRaises(ValidationError):
            self.HrEmployee.create({
                'name': 'Abigail Peterson',
                'names': 'Abigail',
                'surnames': 'Peterson',
                'known_as': 'Abigail',
                'document_type': '41',
                'identification_id': '12025202'
            })

    def test_validation_passport_successfully(self):
        newEmployee = self.HrEmployee.create({
            'name': 'Abigail Peterson',
            'names': 'Abigail',
            'surnames': 'Peterson',
            'known_as': 'Abigail',
            'document_type': '41',
            'identification_id': '12a02c2v2'
        })

    def test_validation_stranger_document_alphanumeric(self):
        with self.assertRaises(ValidationError):
            self.HrEmployee.create({
                'name': 'Abigail Peterson',
                'names': 'Abigail',
                'surnames': 'Peterson',
                'known_as': 'Abigail',
                'document_type': '22',
                'identification_id': '12a02vs'
            })

    def test_validation_stranger_document_length(self):
        with self.assertRaises(ValidationError):
            self.HrEmployee.create({
                'name': 'Abigail Peterson',
                'names': 'Abigail',
                'surnames': 'Peterson',
                'known_as': 'Abigail',
                'document_type': '22',
                'identification_id': '1202'
            })

    def test_validation_stranger_document_success(self):
        employee = self.HrEmployee.create({
            'name': 'Abigail Peterson',
            'names': 'Abigail',
            'surnames': 'Peterson',
            'known_as': 'Abigail',
            'document_type': '22',
            'identification_id': '25412365'
        })

    def test_validation_document_type_error(self):
        with self.assertRaises(ValidationError):
            self.HrEmployee.create({
                'name': 'Abigail Peterson',
                'names': 'Abigail',
                'surnames': 'Peterson',
                'known_as': 'Abigail',
                'document_type': '30',
                'identification_id': '25412365'
            })

    def test_validate_OT_document_type(self):
        self.HrEmployee.create({
            'name': 'Abigail Peterson',
            'names': 'Abigail',
            'surnames': 'Peterson',
            'known_as': 'Abigail',
            'document_type': 'OT',
            'identification_id': '25412365'
        })

    def test_validate_document_type_required(self):
        with self.assertRaises(ValidationError):
            self.HrEmployee.create({
                'name': 'Abigail Peterson',
                'names': 'Abigail',
                'surnames': 'Peterson',
                'known_as': 'Abigail',
                'identification_id': '1234567895'
            })

    def test_validate_whitout_identification_id(self):
        with self.assertRaises(ValidationError):
            self.HrEmployee.create({
                'name': 'Abigail Peterson',
                'names': 'Abigail',
                'surnames': 'Peterson',
                'known_as': 'Abigail',
                'document_type': 'OT'
            })

    def test_validate_whitout_names(self):
        with self.assertRaises(ValidationError):
            self.HrEmployee.create({
                'name': 'Abigail Peterson',
                'surnames': 'Peterson',
                'known_as': 'Abigail',
                'document_type': 'OT'
            })

    def test_validate_whitout_surnames(self):
        with self.assertRaises(ValidationError):
            self.HrEmployee.create({
                'name': 'Abigail Peterson',
                'names': 'Abigail',
                'known_as': 'Abigail',
                'document_type': 'OT'
            })

    def test_validate_whitout_known_as(self):
        with self.assertRaises(ValidationError):
            self.HrEmployee.create({
                'name': 'Abigail Peterson',
                'names': 'Abigail',
                'surnames': 'Peterson',
                'document_type': 'OT'
            })

    def create_account_analytics(self):
        self.center_cost1 = self.env['account.analytic.account'].create({
            'name': 'Desarrollo',
            'code': 'dev'
        })
        self.center_cost2 = self.env['account.analytic.account'].create({
            'name': 'Administracion',
            'code': 'admin'
        })
    
    def test_center_cost_constraint(self):
        self.create_account_analytics()
        with self.assertRaises(ValidationError):
            new_employee = self.HrEmployee.create({
                'name': 'Abigail Peterson',
                'names': 'Abigail',
                'surnames': 'Peterson',
                'document_type': '13',
                'identification_id': '1234567895',
                'known_as': 'Abigail',
                'birthday': date(1993, 11, 20),
                'spouse_birthdate': date(1993, 11, 20),
                'employee_center_cost_ids': [(0, 0, {
                    'percentage': 101.00,
                    'account_analytic_id': self.center_cost1.id
                })]
            })
    
    def test_compute_contract_type(self):
        hr_payroll_structure_type = self.env['hr.payroll.structure.type'].create({
            'name': "Test Type",
            'wage_type': "monthly",
            "is_novelty": True
        })

        new_employee2 = self.HrEmployee.create({
            'name': 'Abigail Peterson',
            'names': 'Abigail',
            'surnames': 'Peterson',
            'document_type': '13',
            'identification_id': '1234567895',
            'known_as': 'Abigail',
            'birthday': date(1993, 11, 20),
            'spouse_birthdate': date(1993, 11, 20),
            'contract_ids': [(0, 0, {
                'name': "Contract Test",
                'rate': 4.3500,
                'date_start': datetime.now(),
                'date_end': datetime.now()+timedelta(days=365),
                'structure_type_id': hr_payroll_structure_type.id,
                'state': 'open',
                'wage': 3000000,
            })]
        })
        new_employee2._compute_contract_type()
    
    def test_compute_contract_type_draft(self):
        hr_payroll_structure_type = self.env['hr.payroll.structure.type'].create({
            'name': "Test Type",
            'wage_type': "monthly",
            "is_novelty": True
        })

        new_employee3 = self.HrEmployee.create({
            'name': 'Abigail Peterson',
            'names': 'Abigail',
            'surnames': 'Peterson',
            'document_type': '13',
            'identification_id': '1234567895',
            'known_as': 'Abigail',
            'birthday': date(1993, 11, 20),
            'spouse_birthdate': date(1993, 11, 20),
            'contract_ids': [(0, 0, {
                'name': "Contract Test",
                'rate': 4.3500,
                'date_start': datetime.now(),
                'date_end': datetime.now()+timedelta(days=365),
                'structure_type_id': hr_payroll_structure_type.id,
                'state': 'draft',
                'wage': 3000000,
            })]
        })
        new_employee3._compute_contract_type()
    
    def test_compute_contract_type_no_contract(self):
        new_employee1 = self.HrEmployee.create({
            'name': 'Abigail Peterson 2',
            'names': 'Abigail',
            'surnames': 'Peterson',
            'document_type': '13',
            'identification_id': '1234567895',
            'known_as': 'Abigail',
            'birthday': date(1993, 11, 20),
            'spouse_birthdate': date(1993, 11, 20),
            'contract_ids': False
        })
        new_employee1._compute_contract_type()
    
    def test_check_workload(self):
        new_employee4 = self.HrEmployee.create({
            'name': 'Abigail Peterson 2',
            'names': 'Abigail',
            'surnames': 'Peterson',
            'document_type': '13',
            'identification_id': '1234567895',
            'known_as': 'Abigail',
            'birthday': date(1993, 11, 20),
            'spouse_birthdate': date(1993, 11, 20),
            'contract_ids': False
        })
        new_employee4._check_workload()
    
    """
    def test_valid_center_cost(self):
        config = self.env['res.config.settings'].create({})
        config.percentage_workload = 150
        config.execute()
        self.env['res.config.settings']
        self.create_account_analytics()
        new_employee = self.HrEmployee.create({
            'name': 'Abigail Peterson',
            'names': 'Abigail',
            'surnames': 'Peterson',
            'document_type': '13',
            'identification_id': '1234567895',
            'known_as': 'Abigail',
            'birthday': date(1993, 11, 20),
            'spouse_birthdate': date(1993, 11, 20),
            'employee_center_cost_ids': [(0, 0, {
                'percentage': 150.00,
                'account_analytic_id': self.center_cost1.id
            })]
        })
    """
