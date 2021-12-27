# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrRecruitmentResponsabilitiesCharge(models.Model):
    _name = 'hr.recruitment.responsabilities.charge'
    _description = _('Recruitment Responsabilities Charge configuration')

    name = fields.Char(
        _('Responsabilities Charge Name'),
        required=True)
    code = fields.Char(string=_('Code'))
    active = fields.Boolean(string=_('Active'))
    description = fields.Char(string=_('Description'))
