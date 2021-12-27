# -*- coding: utf-8 -*-
from datetime import date, datetime, timedelta
from odoo.exceptions import ValidationError
from .common import (TestHrRecruitmentScheduling)


class TestHrApplicant(TestHrRecruitmentScheduling):

    def setUp(self):
        super(TestHrApplicant, self).setUp()

    def test_applicant(self):
        self.applicant.action_makeMeeting()

    def test_applicant_with_assigned(self):
        self.applicant.write({
            'stage_id': self.stage_job2.id
        })
        self.applicant.action_makeMeeting()
