# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrRecruitmentOrganizationalCompetencies(models.Model):
    _name = 'hr.recruitment.organizational.competencies'
    _description = _('Organizational Competencies configuration')

    name = fields.Char(
        _('Organizational Competencies Name'),
        required=True)
    code = fields.Char(string=_('Code'))
    active = fields.Boolean(string=_('Active'))
    description = fields.Char(string=_('Description'))
