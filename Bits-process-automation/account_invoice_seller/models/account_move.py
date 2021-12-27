# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import ValidationError


class AccountInvoiceSeller(models.Model):
    _inherit = 'account.move'
    _description = 'Extended Account Move'

    @api.onchange('partner_id')
    def _onchange_partner_user_commercial(self):
        if self.partner_id and self.partner_id.user_id:
            self.invoice_user_id = self.partner_id.user_id
        elif self.partner_id and not self.partner_id.user_id:
            self.invoice_user_id = False
            raise ValidationError(
                _('The client was not assigned to one seller.')
            )

    @api.model
    def create(self, vals):
        """Update the registry when a new bill is created."""
        ''' Only billings of customer type'''
        if (self.env.context.get('default_type', False)
                in ('out_invoice', 'out_refund')):
            if not vals.get('partner_id', False):
                raise ValidationError(
                    _('You can select the client with seller')
                )
            partner_id = self.env['res.partner'].browse(vals.get('partner_id'))
            vals['invoice_user_id'] = partner_id.user_id.id

            if not vals.get('invoice_user_id', False):
                raise ValidationError(
                    _('The client was not assigned to one seller.')
                )
        created_val = super(AccountInvoiceSeller, self).create(vals)
        return created_val
