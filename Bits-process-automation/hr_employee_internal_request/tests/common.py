from datetime import datetime, timedelta
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo.fields import Date


class TestHrEmployeeInternalRequestBase(TransactionCase):

    def setUp(self):
        super(TestHrEmployeeInternalRequestBase, self).setUp()
        self.hr_job = self.env['hr.job']
        self.hr_employee = self.env['hr.employee']
        self.res_partner = self.env['res.partner']
        self.request = self.env['hr.employee.internal.request']
        self.request_stages = self.env['hr.employee.internal.request.stages']
        self.request_wizard = self.env['hr.employee.internal.request.wizard']

        self.job = self.hr_job.create({
            "name": "Adminitrador"
        })

        self.partner = self.res_partner.create({
            'name': 'Test Partner',
            'email': 'example@email.com'
        })

        self.employee = self.hr_employee.create({
            'name': 'Test Employee',
            'job_id': self.job.id,
            'address_home_id': self.partner.id
        })

        self.stage = self.env.ref(
            'hr_employee_internal_request.internal_request_stage_1')
        self.stage_cancel = self.env.ref(
            'hr_employee_internal_request.internal_request_stage_6')

        self.template = self.env.ref(
            'hr_employee_internal_request.template_internal_request_sent')

        self.stage.write({
            'template_id': self.template.id
        })

        self.internal_request = self.request.create({
            "name": "Internal Request",
            "job_position": self.job.id,
            "stage_id": self.stage.id
        })
