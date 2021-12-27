# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrRecruitmentTechnicalTechnologicalCompetencies(models.Model):
    _name = 'hr.recruitment.technical.technological.competencies'
    _description = _(
        'Recruitment Technical Technological Competencies configuration')

    name = fields.Char(
        _('Technical Technological Competencies Name'),
        required=True)
    code = fields.Char(string=_('Code'))
    active = fields.Boolean(string=_('Active'))
    description = fields.Char(string=_('Description'))
