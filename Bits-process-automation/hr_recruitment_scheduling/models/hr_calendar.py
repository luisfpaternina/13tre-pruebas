# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class HrRecruitmentSchedulingCalendar(models.Model):
    _inherit = 'calendar.event'

    def write(self, values):
        defaults = self.default_get(
            ['activity_ids', 'res_model_id', 'res_id', 'user_id'])

        if not self.applicant_id:
            values['applicant_id'] = defaults.get('applicant_id')

        return super(HrRecruitmentSchedulingCalendar, self).write(values)
