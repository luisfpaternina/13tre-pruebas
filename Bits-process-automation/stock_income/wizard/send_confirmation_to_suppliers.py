# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SendConfirmationSuppliers(models.TransientModel):
    _name = "send.confirmation.to.suppliers"
    _inherits = {'mail.compose.message': 'composer_id'}
    _description = 'Sending confirmation to suppliers'

    is_email = fields.Boolean('Email', default=True)
    is_print = fields.Boolean('Print', default=True)
    printed = fields.Boolean('Is Printed', default=False)
    stock_picking_ids = fields.Many2many(
        'stock.picking',
        'stock_picking_send_confirmation_rel',
        string="Stock ids",
        invisible=True
    )
    composer_id = fields.Many2one(
        'mail.compose.message',
        string="Composer",
        required=True,
        ondelete='cascade'
    )
    template_id = fields.Many2one(
        'mail.template',
        'Use template',
        domain=[('model_id', '=', 'stock.picking')],
        index=True
    )

    @api.onchange('stock_picking_ids')
    def _compute_composition_mode(self):
        self.ensure_one()
        mode = 'comment' if len(self.stock_picking_ids) == 1 else 'mass_mail'
        self.composer_id.composition_mode = mode

    @api.model
    def default_get(self, fields):
        res = super(SendConfirmationSuppliers, self).default_get(fields)
        res_ids = self._context.get('active_ids')
        composer = self.env['mail.compose.message'].create({
            'composition_mode': (
                'comment' if len(res_ids) == 1 else 'mass_mail'
            )
        })
        res.update({
            'stock_picking_ids': res_ids,
            'composer_id': composer.id
        })
        return res

    @api.onchange('template_id')
    def onchange_template_id(self):
        for wizard in self:
            if wizard.composer_id:
                wizard.composer_id.template_id = wizard.template_id.id
                wizard.composer_id.onchange_template_id_wrapper()

    @api.onchange('is_email')
    def onchange_is_email(self):
        if self.is_email:
            if not self.composer_id:
                res_ids = self._context.get('active_ids')
                self.composer_id = self.env['mail.compose.message'].create({
                    'composition_mode': (
                        'comment' if len(res_ids) == 1 else 'mass_mail'
                    ),
                    'template_id': self.template_id.id
                })
            self.composer_id.onchange_template_id_wrapper()

    def _print_document(self):
        self.ensure_one()
        action = self.stock_picking_ids.print_receipt_confirmation()
        action.update({'close_on_report_download': True})
        return action

    def _send_email(self):
        if self.is_email:
            self.composer_id.send_mail()

    def send_and_print_action(self):
        for record in self.stock_picking_ids:
            if record.state != 'done':
                raise UserError(
                    _(
                        "To confirm that the product or service \
                        was received, it must be 'done'"
                    )
                )
        self.ensure_one()
        self._send_email()
        if self.is_print:
            return self._print_document()
        return {'type': 'ir.actions.act_window_close'}
