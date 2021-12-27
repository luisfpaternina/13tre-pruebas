# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrJob(models.Model):
    _inherit = 'hr.job'

    department_ids = fields.Many2many(
        'hr.department',
        'hr_job_department_table',
        string='Departments')
