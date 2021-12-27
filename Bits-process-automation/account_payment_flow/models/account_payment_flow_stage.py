# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountPaymentFlowStage(models.Model):
    _name = 'account.payment.flow.stage'
    _description = _('Payment stage configuration interface')

    name = fields.Char(
        'Stage Name',
        required=True,
        translate=True)
    close = fields.Boolean(
        'Closing Stage',
        help='When is checked this stage are considered as done. \
            This is used when flow is finished')
    sequence = fields.Integer(
        'Succession',
        default=1,
        help="Used to order stages. Lower is better.")
    fold = fields.Boolean(
        'Folded in Kanban',
        help='This stage is folded in the kanban view when \
        there are no records in that stage to display.')
    template_id = fields.Many2one(
        'mail.template', 'Email Template',
        domain="[('model', '=', 'account.payment.flow')]",
        help="Automated email sent to the partner assigned when \
        the payment reaches this stage.")
    partner_id = fields.Many2one(
        'res.partner',
        string="Assigned to"
    )
    team_ids = fields.One2many(
        'account.payment.flow.stage.team',
        'team_stage_rel',
        string='Team')
