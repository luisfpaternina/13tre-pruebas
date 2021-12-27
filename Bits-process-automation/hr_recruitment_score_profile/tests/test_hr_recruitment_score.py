from datetime import date
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.addons.hr_recruitment_score_profile.tests.common \
    import TestHrRecruitmentScoreProfile
from odoo.exceptions import UserError, ValidationError


class TestHrRecruitmentScoreProfileRun(TestHrRecruitmentScoreProfile):
    def setUp(self):
        super(TestHrRecruitmentScoreProfileRun, self).setUp()
       
    def test_compute_test_result_count(self):
        applicant = self.InheritApplicant._compute_test_result_count()
    
    def test_compute_test_result_lines(self):
        compute_test_results = self.HrRecruitmentScoreTestResults.compute_test_result_lines()
    
    def test_onchange_mjs(self):
        onchange = self.HrRecruitmentScoreTestResults._onchange_mjs()
    
    def test_compute_test_result_lines(self):
        onchange_test_results = self.HrRecruitmentScoreTestResults.compute_test_result_lines()
    
    def test_calculated_weighted_average(self):
        calculated_weighted_average = self.HrRecruitmentScoreTestResults._calculated_weighted_average()
    
    def test_calculated_total(self):
        calculated_total = self.HrRecruitmentScoreTestResults._calculated_total()
        
    def test_calculated_weighted_average_related(self):
        profile_lines = self.HrRecruitmentScoreProfile._calculated_weighted_average_related()
    
    def test_calculated_total(self):
        calculated_total = self.HrRecruitmentScoreProfile._calculated_total()
    
    def test_compute_test_result_lines_profile(self):
        compute_test_results_profile = self.HrRecruitmentScoreProfile.compute_test_result_lines()
    
    
        
    
    
        
    
    
    
    
    
    
    
    