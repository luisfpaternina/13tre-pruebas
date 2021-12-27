# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class HrJob(models.Model):
    _inherit = 'hr.job'
    _description = 'Jobs'

    surveys_id = fields.Many2many('survey.survey', 'job_survey_rel', 'job_id', 'survey_id', 'Interviews',tracking=True)
