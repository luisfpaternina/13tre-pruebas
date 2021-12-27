from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class TestSocialSecurity(TransactionCase):

    def setUp(self):
        super(TestSocialSecurity, self).setUp()
        self.social_security = self.env['social.security']
        self.employee_id = self.env['hr.employee']
        self.contratc_id = self.env['hr.contract']

    def test_enter_data(self):
        new_social_security = self.social_security.create({
            'code': 'TST001',
            'name': 'Prueba de Ingreso de datos',
            'entity_type': 'arl'
        })

    def test_onchange_risk_class(self):
        new_employee = self.employee_id.create({
            'name': 'Benito'
        })

        new_ref = self.env.ref(
            'hr_employee_social_security.entity_165')

        new_contract = self.contratc_id.create({
            'name': 'Contract test',
            'employee_id': new_employee.id,
            'name': "Contract Test",
            'date_start': datetime.now(),
            'date_end': datetime.now()+timedelta(days=365),
            'wage': 800000,
            'risk_class': new_ref.id
        })

        new_contract._onchange_risk_class()
