# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrRecruitmentLevel(models.Model):
    _name = 'hr.recruitment.experience'
    _description = _('Recruitment experience configuration')

    name = fields.Char(
        _('Name'),
        required=True)
