# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountPaymentFlowStageTeam(models.Model):
    _name = 'account.payment.flow.stage.team'
    _description = _('Model for flow stage teams')

    team_stage_rel = fields.Many2one(
        'account.payment.flow.stage',
        string='Flow Stage')
    name = fields.Char(
        string='Name')
    group = fields.Many2one(
        'res.groups',
        string='Group')
