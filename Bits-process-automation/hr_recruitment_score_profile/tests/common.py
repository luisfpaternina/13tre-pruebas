# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.fields import Date
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestHrRecruitmentScoreProfile(TransactionCase):

    def setUp(self):
        super(TestHrRecruitmentScoreProfile, self).setUp()
        self.HrRecruitmentScoreProfile = self.env['hr.recruitment.score.profile']
        self.HrRecruitmentScoreProfileLines = self.env['hr.recruitment.score.profile.lines']
        self.HrRecruitmentScoreSkills = self.env['hr.recruitment.score.skills']
        self.HrRecruitmentScoreSkillsLines = self.env['hr.recruitment.score.lines.skills']
        self.HrRecruitmentScoreTechnologies = self.env['hr.recruitment.score.technologies']
        self.HrRecruitmentScoreTestResults = self.env['hr.recruitment.score.test.results']
        self.HrRecruitmentScoreTestResultsLines = self.env['hr.recruitment.score.test.results.lines']
        self.InheritApplicant = self.env['hr.applicant']
        self.ApplicantLines = self.env['hr.applicant.lines']
        
        
        self.applicant = self.InheritApplicant.create({
            'name': 'Luis Felipe Paternina',
        })
        
        self.score_profile = self.HrRecruitmentScoreProfile.create({
            'name': "Test profile",
            'code': "00223013",
            'active': True
        })

        self.score_skills = self.HrRecruitmentScoreSkills.create({
            'name': "python",
            'code': "3013564",
            'active': True,
            'percentage': 10.3,
            'description': "test description"
        })

        self.score_technologies = self.HrRecruitmentScoreTechnologies.create({
            'name': "Test technology",
            'code': "1993450",
            'description': "description technology",
            'active': True
        })
        
        self.score_test_results = self.HrRecruitmentScoreTestResults.create({
            'applicant_id': self.HrRecruitmentScoreTestResults.applicant_id,
            'tecnology_id': self.HrRecruitmentScoreTestResults.tecnology_id,
            'profile_id': self.HrRecruitmentScoreTestResults.profile_id,
        })
        
        self.test_result_line = self.HrRecruitmentScoreTestResultsLines.create({
            'percentage': 20.0,
            'margen': 20.0
        })
        
        self.sequence = self.HrRecruitmentScoreProfile.create({
            'code': '000001'
        })
        
  
        
    
    
    