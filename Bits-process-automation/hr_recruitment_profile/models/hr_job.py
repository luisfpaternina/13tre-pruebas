# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrJob(models.Model):
    _inherit = 'hr.job'

    job_level = fields.Char(
        string='Job level')
    education = fields.Char(
        string='Education')
    apprenticeship = fields.Char(
        string='Apprenticeship')
    total_time = fields.Char(
        string='Total time')
    specific_time = fields.Char(
        string='Specific time')
    skills = fields.Char(
        string='Skills')
