# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrRecruitmentHasPositionsInChargeCompetencies(models.Model):
    _name = 'hr.recruitment.has.positions.in.charge.competencies'
    _description = _(
        'Recruitment has Positions in Charge Competencies configuration')

    position_in_charge_ids = fields.Many2one(
        'hr.recruitment.positions.in.charge.competencies',
        string=_('Positions in Charge Competencies'))
    charge_id = fields.Many2one('hr.job', string=_(
        'Charge'))
    calification = fields.Selection(
        [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
        string='Calification')
    level = fields.Selection([('i','II'),('ii','II'),('iii','III'),('iv','IV'),('v','V')],string="Level")
