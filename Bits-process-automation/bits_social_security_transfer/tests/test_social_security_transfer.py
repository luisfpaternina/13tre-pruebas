from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestSocialSecurity(TransactionCase):

    def setUp(self):
        super(TestSocialSecurity, self).setUp()
        self.ss_transfers = self.env['social.security.transfer']
        self.hr_employee = self.env['hr.employee']
        self.employee = self.hr_employee.create({
            'name': "Test Payroll News",
            'document_type': '13',
            'identification_id': "75395146",
            'names': 'NOMBRE1 NOMBRE2',
            'surnames': 'APELLIDO1 APELLIDO2',
            'known_as': 'SuperCode',
        })

    # ('entity_type', '=', 'arl')
    def test_enter_data(self):
        old = self.env['social.security'].search([
            ('entity_type', '=', 'arl'),
            ('code', '=', '0')], limit=1)

        new = self.env['social.security'].search([
            ('entity_type', '=', 'arl'),
            ('code', '=', '14-11')], limit=1)

        new_social_security = self.ss_transfers.create({
            'employee_id': self.employee.id,
            'request_date': "2020-04-01",
            'social_security_old': old.id,
            'social_security_new': new.id,
            'entity_type': 'arl'
        })
