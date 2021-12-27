# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.fields import Date
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestHrRecruitmentInterviewSurvey(TransactionCase):
    def setUp(self):
        super(TestHrRecruitmentInterviewSurvey, self).setUp()
        self.survey_input = self.env['survey.user_input']
        self.wizard_survey_print = self.env['wizard.survey.print']
        self.survey = self.env['wizard.survey']

    def test_default_applicantlt_job(self):
        self.survey._default_applicantlt_job()
    
    def test_default_job(self):
        self.survey._default_job()
    
    def test_default_survey(self):
        self.survey._default_survey()
    
    def test_action_start_survey(self):
        self.survey.action_start_survey()
    
    def test_default_applicant_id(self):
        self.surveyprint.test_default_applicant_id()
    
    def test_default_input(self):
        self.surveyprint._default_input()
    
    def test_action_print_survey(self):
        self.surveyprint.action_print_survey()
        
        
