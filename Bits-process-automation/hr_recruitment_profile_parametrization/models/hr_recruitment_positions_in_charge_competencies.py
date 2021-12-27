# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrRecruitmentPositionsInChargeCompetencies(models.Model):
    _name = 'hr.recruitment.positions.in.charge.competencies'
    _description = _(
        'Recruitment Positions In Charge Competencies Configuration')

    name = fields.Char(
        _(' Name'),
        required=True)
    code = fields.Char(string=_('Code'))
    active = fields.Boolean(string=_('Active'))
    description = fields.Char(string=_('Description'))
