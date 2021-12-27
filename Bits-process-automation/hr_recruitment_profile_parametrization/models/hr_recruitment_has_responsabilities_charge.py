# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrRecruitmentHasResponsabilitiesCharge(models.Model):
    _name = 'hr.recruitment.has.responsabilities.charge'
    _description = _('Recruitment Has Responsabilities Charge configuration')

    responsabilities_id = fields.Many2one(
        'hr.recruitment.responsabilities.charge',
        string=_('Responsabilities Charge'))
    charge_id = fields.Many2one('hr.job',
                                string=_('Charge'))
    calification = fields.Selection(
        [('low', 'Baja'), ('med', 'Media'), ('high', 'Alta')],
        string=_('Calification'))
