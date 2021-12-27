from datetime import date
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo.addons.hr_recruitment_profile_parametrization.tests.common \
    import TestRecruitmentProfileParametrization
from odoo.exceptions import UserError, ValidationError


class TestHrRecruitmentSpecificCompet(TestRecruitmentProfileParametrization):

    def setUp(self):
        super(TestHrRecruitmentSpecificCompet, self).setUp()

    # Space for future computed field or functions
