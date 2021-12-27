# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrRecruitmentHasSpecificCompetencies(models.Model):
    _name = 'hr.recruitment.has.specific.competencies'
    _description = _('Recruitment Has Specific Competencies Configuration')

    specific_id = fields.Many2one(
        'hr.recruitment.specific.competencies',
        string=_('Specific Competencies'))
    charge_id = fields.Many2one('hr.job',
                                string=_('Charge'))
    calification = fields.Selection(
        [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
        string='Calification')
    level = fields.Selection(
        [('i', 'II'), ('ii', 'II'), ('iii', 'III'), ('iv', 'IV'), ('v', 'V')], string="Level")
