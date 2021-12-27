# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrRecruitmentWorkConditions(models.Model):
    _name = 'hr.recruitment.work.conditions'
    _description = _('Recruitment Work Conditions configuration')

    name = fields.Char(
        _('Work Conditions Name'),
        required=True)
    code = fields.Char(string=_('Code'))
    active = fields.Boolean(string=_('Active'))
    description = fields.Char(string=_('Description'))
