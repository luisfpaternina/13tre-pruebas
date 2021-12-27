# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    general_state = fields.Selection([
        ('none', 'None'),
        ('reviewed', 'Reviewed'),
        ('draft', 'Draft')],
        default='draft')

    def get_restrict_action_move(self, action_name):
        restrict_actions = self.env['ir.actions.restrict'].search(
            [('model', '=', self._name), ('action_name', '=', action_name)])
        if restrict_actions:
            restrict_actions.validate_user_groups()

    def action_general_state_approve(self):
        self.get_restrict_action_move('action_general_state_approve')
        return self.write({'general_state': 'reviewed'})

    def action_invoice_register_payment(self):
        if self.general_state != 'reviewed':
            raise UserError(_(
                "The bill needs to be reviewed to register payment."))
        return super(AccountMove, self).action_invoice_register_payment()
