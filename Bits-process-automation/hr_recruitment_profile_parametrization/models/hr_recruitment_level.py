# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrRecruitmentLevel(models.Model):
    _name = 'hr.recruitment.level'
    _description = _('Recruitment aptitudes level configuration')

    name = fields.Char(
        _('Level Name'),
        required=True)
