import base64
from io import BytesIO, StringIO
from odoo.tests.common import TransactionCase
from odoo.addons.hr_recruitment_postulation.controllers.controllers import (
    HrRecruitmentPostulation)
from unittest.mock import patch, Mock
from odoo.addons.website.tools import MockRequest
from odoo.exceptions import ValidationError
from odoo.http import request
from werkzeug.datastructures import FileStorage
import odoo.tests


class TestHrRecruitmentPostulation(TransactionCase):

    # Create internal request
    # Create Object hr_applicant
    def setUp(self):
        super(TestHrRecruitmentPostulation, self).setUp()

        self.hr_job = self.env['hr.job']

        self.model_applicant = self.env['ir.model']\
            .search([('model', '=', 'hr.applicant')])

        self.model_employee = self.env['ir.model']\
            .search([('model', '=', 'hr.employee')])

        self.url = ('odoo.addons.website_form.controllers.main')
        # Create job post
        self.test_job = self.hr_job.create({
            'name': 'test_job'
        })
        self.test_job_two = self.hr_job.create({
            'name': 'test_job_two'
        })

        self.return_value = dict(
            status='accepted',
            transactionID='000001')

        self.values = {
            'name': 'Test Name',
            'partner_name': 'applicant name test',
            'email_from': 'email@test.com',
            'partner_phone': '2352123',
            'description': 'test description',
            'job_id': self.test_job.id
        }

        self.values_two = {
            'name': 'Test Name',
            'partner_name': 'applicant name test',
            'email_from': 'email@test.com',
            'partner_phone': '2352123',
            'description': 'test description',
            'job_id': self.test_job_two.id
        }

    def test_insert_record(self):
        controller = HrRecruitmentPostulation()
        self.hr_internal = self.env['hr.employee.internal.request']
        self.hr_internal_stage = self\
            .env['hr.employee.internal.request.stages']

        self.internal_stage = self.hr_internal_stage.create(
            {'name': 'Stage 4', 'sequence': 4})

        self.internal = self.hr_internal.create({
            'name': 'Internal Request',
            'job_position': self.test_job.id,
            'stage_id': self.internal_stage.sequence
        })
        with MockRequest(self.env):
            with patch(self.url, new=Mock(return_value=self.return_value)):
                controller.insert_record(
                    request, self.model_applicant, self.values, custom='')

    def test_insert_attachment(self):
        controller = HrRecruitmentPostulation()

        applicant = self.env['hr.applicant'].create(self.values)

        fileB = BytesIO()
        fileB.write(b"New File for attachments")
        fileB.seek(0)

        filestorage = FileStorage(
            filename="file.pdf", stream=fileB, content_type='application/pdf',
            name='file')
        filestorage.field_name = "Resume"

        files = [filestorage]

        with MockRequest(self.env):
            with patch(self.url, new=Mock(return_value=self.return_value)):
                controller.insert_record(
                    request, self.model_applicant, self.values, custom='')
                controller.insert_attachment(
                    self.model_applicant, applicant.id, files)

    def test_insert_attachment_without_files(self):
        controller = HrRecruitmentPostulation()
        applicant = self.env['hr.applicant'].create(self.values)
        with MockRequest(self.env):
            with patch(self.url, new=Mock(return_value=self.return_value)):
                controller.insert_attachment(
                    self.model_employee, applicant.id, [])

    def test_write(self):
        self.hr_internal = self.env['hr.employee.internal.request']
        self.hr_internal_stage = self\
            .env['hr.employee.internal.request.stages']

        self.internal_stage = self.hr_internal_stage.create(
            {'name': 'Stage 4', 'sequence': 4})

        self.hr_technology = self.env['hr.recruitment.score.technologies']

        self.technology = self.hr_technology.create({
            'name': 'Technology Odoo',
            'code': '000120'
        })

        self.internal = self.hr_internal.create({
            'name': 'Internal Request',
            'job_position': self.test_job.id,
            'stage_id': self.internal_stage.sequence,
            'code': '0001',
            'tecnology_id': self.technology.id
        })
        applicant = self.env['hr.applicant'].create(self.values)

        # Testing onchange event
        applicant._onchange_job_id()
        applicant.write({'partner_name': 'applicant name test 1',
                         'job_id': self.test_job_two.id})

    def test_write_internal(self):
        self.hr_internal = self.env['hr.employee.internal.request']
        self.hr_internal_stage = self\
            .env['hr.employee.internal.request.stages']

        self.internal_stage = self.hr_internal_stage.create(
            {'name': 'Stage 4', 'sequence': 4})

        self.internal = False
        applicant = self.env['hr.applicant'].create(self.values_two)

        # Testing onchange event
        applicant._onchange_job_id()
        applicant.write({'partner_name': 'applicant name test 2',
                         'job_id': self.test_job_two.id})
        applicant.write({'partner_name': 'applicant name test 1',
                         'job_id': self.test_job.id})
