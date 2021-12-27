# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo.fields import Date
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestHrRecruitmentAppraisalRequest(TransactionCase):
    def setUp(self):
        super(TestHrRecruitmentAppraisalRequest, self).setUp()
        self.hr_appraisal = self.env['hr.recruitment.appraisal.request']
        self.appraisal = self.hr_appraisal.create({
            'name': "Luis Felipe Paternina"
        })
        
