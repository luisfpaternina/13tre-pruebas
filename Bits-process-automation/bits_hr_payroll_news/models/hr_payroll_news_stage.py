# Part of Bits. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class HrPayrollNewsStage(models.Model):
    _name = 'hr.payroll.news.stage'
    _description = 'bits_payroll_news.bits_payroll_news_stage'

    _rec_name = 'name'
    _order = "sequence, name, id"

    name = fields.Char('Stage Name', required=True, translate=True)
    sequence = fields.Integer(
        'Succession',
        default=1,
        help="Used to order stages. Lower is better.")
    is_won = fields.Boolean('Is Won Stage?')
    requirements = fields.Text(
        'Internal requirements',
        help="Enter here the internal requirements for this stage \
        (ex: Offer sent to customer). It will appear as a tooltip \
        over the stage's name.")
    fold = fields.Boolean(
        'Folded',
        help='This stage is folded in the kanban view when \
        there are no records in that stage to display.')
    legend_blocked = fields.Char(
        'Red Kanban Label',
        default=lambda s: _('Blocked'),
        translate=True,
        required=True,
        help='Override the default value displayed for the blocked \
        state for kanban selection, when the task or issue is in that stage.')
    legend_done = fields.Char(
        'Green Kanban Label',
        default=lambda s: _('Ready for Next Stage'),
        translate=True,
        required=True,
        help='Override the default value displayed for the done state \
        for kanban selection, when the task or issue is in that stage.')
    legend_normal = fields.Char(
        'Grey Kanban Label',
        default=lambda s: _('In Progress'),
        translate=True,
        required=True,
        help='Override the default value displayed for the normal \
        state for kanban selection, when the task or issue is in that stage.')

    is_approved = fields.Boolean('Is approved stage?')
