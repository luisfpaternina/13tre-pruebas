# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrRecruitmentHasOrganizationalCompetencies(models.Model):
    _name = 'hr.recruitment.has.organizational.competencies'
    _description = _(
        'Recruitment Has Organizational Competencies configuration')

    charge_id = fields.Many2one('hr.job', string=_(
        'Post Job'))
    organizational_competencies_id = fields.Many2one(
        'hr.recruitment.organizational.competencies',
        string=_('Organizational Competencies'))
    calification = fields.Selection(
        [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
        string='Calification')
    level = fields.Selection([('i','II'),('ii','II'),('iii','III'),('iv','IV'),('v','V')],string="Level")
