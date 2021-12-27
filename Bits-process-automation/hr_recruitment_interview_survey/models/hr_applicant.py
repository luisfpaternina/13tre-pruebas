# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'
    _description = 'Applicant'

    is_need_interview = fields.Boolean(string="Need interviews?")
