# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo.fields import Date
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestHrJobProfileReport(TransactionCase):
    def setUp(self):
        super(TestHrJobProfileReport, self).setUp()
        self.hr_job = self.env['hr.job']
        self.documetation_version = self.env['document.version.control']
        self.job = self.hr_job.create({
            'name': "Test Job"
        })
        self.control_version = self.documetation_version.create({
            'name': "Version Control",
            'is_implement_model': True,
            'job_id': self.job.id
        })

    def test_get_control_version(self):
        self.job._get_control_version()

    def test_documentation_version_create(self):
        self.control_version._get_currect_model()
        self.documetation_version.create({
            'name': "Version Control",
            'is_implement_model': True,
            'job_id': self.job.id,
            'version': 2.0
        })
        self.documetation_version.create({
            'name': "Version Control",
            'job_id': self.job.id,
            'version': 2.0
        })
