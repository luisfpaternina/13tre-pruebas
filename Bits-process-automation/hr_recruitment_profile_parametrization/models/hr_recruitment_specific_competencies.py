# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrRecruitmentSpecificCompetencies(models.Model):
    _name = 'hr.recruitment.specific.competencies'
    _description = _('Recruitment Specific Competencies configuration')

    name = fields.Char(
        _('Specific Competencies Name'),
        required=True)
    code = fields.Char(string=_('Code'))
    active = fields.Boolean(string=_('Active'))
    description = fields.Char(string=_('Description'))
