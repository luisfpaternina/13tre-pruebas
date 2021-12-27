from datetime import datetime, date
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestHrEmployeeDocument(TransactionCase):

    def setUp(self):
        super(TestHrEmployeeDocument, self).setUp()
        self.hr_employee_document_type = self.env['hr.employee.document.type']
        self.hr_employee = self.env['hr.employee']
        self.employee_document_line = self.env['hr.employee.document.line']
        self.document_type = self.hr_employee_document_type.create({
            'name': "TST TYPE",
            'code': "TSTT"
        })
        self.employee = self.hr_employee.create({
            'name': 'Employee Test'
        })
        self.document_line = self.employee_document_line.create({
            'employee_id': self.employee.id,
            'document_type_id': self.document_type.id,
            'expiration_date': date(2020, 7, 16)
        })

    def test_get_default_company(self):
        self.document_type._get_default_company()
