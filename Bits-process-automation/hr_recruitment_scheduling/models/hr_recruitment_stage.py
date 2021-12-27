# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrRecruitmentStage(models.Model):
    _inherit = 'hr.recruitment.stage'

    assigned_to = fields.Many2one(
        'res.partner',
        string="Assigned to")
