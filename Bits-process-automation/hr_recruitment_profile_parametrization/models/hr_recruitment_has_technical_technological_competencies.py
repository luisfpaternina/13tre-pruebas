# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrRecruitmentHasTechnicalTechnologicalCompetencies(models.Model):
    _name = 'hr.recruitment.has.technical.technological.competencies'
    _description = _(
        'Recruitment Has Technical Technological Competencies Configuration')

    technical_competencies_id = fields.Many2one(
        'hr.recruitment.technical.technological.competencies',
        string=_('Technical Technological Competencies'))
    charge_id = fields.Many2one('hr.job',
                                string=_('Charge'))
    calification = fields.Selection(
        [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
        string='Calification')
    level = fields.Selection([('i','II'),('ii','II'),('iii','III'),('iv','IV'),('v','V')],string="Level")
