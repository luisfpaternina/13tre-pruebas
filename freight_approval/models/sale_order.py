# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection(
        selection_add=[
            ('draft', 'Quotation'),
            ('sent', 'Quotation Sent'),
            ('waiting_for_approval', 'Waiting For Approval'),
            ('approve_superior', 'Approved By The Superior'),
            ('sale', 'Sales Order'),
            ('done', 'Locked'),
            ('cancel', 'Cancelled'),
        ],
        string='Status',
        readonly=True,
        copy=False,
        index=True,
        track_visibility='onchange',
        default='draft'
    )
    approver_freight_id = fields.Many2one(
        'res.users',
        'Sale Order Freight Approver',
        readonly=True,
        copy=False,
        track_visibility='onchange'
    )

    @api.onchange('order_line', 'partner_id')
    def onchange_order_line(self):
        delivery_line = self.order_line.filtered('is_delivery')
        is_change_delivery_line = False
        for line in delivery_line:
            if line.product_id.lst_price != line.price_unit:
                is_change_delivery_line = True
                break
        if is_change_delivery_line:
            self.recompute_delivery_price = True

    def send_for_approval(self):
        for record in self:
            record.update(
                {
                    'state': 'waiting_for_approval'
                }
            )

    def action_cancel(self):
        context = self.env.context
        if 'rejected_by_a_superior' in context:
            self.message_post(
                body=_(
                    '<i>After the quote was sent for approval, '
                    'it has been <strong>rejected.</strong></i>'
                )
            )

        if self.approver_freight_id:
            self.update({
                'recompute_delivery_price': True
            })

        res = super(SaleOrder, self).action_cancel()
        return res

    def action_confirm_flow(self):
        context = self.env.context
        if 'approve_by_a_superior' in context:
            if 'approve_freight' in context:
                self.message_post(
                    body=_(
                        '<i>After the quote has been sent for approval, '
                        'it has been <strong>approved.</strong></i>'
                    )
                )
                self.approver_freight_id = self.env.user.id
                self.recompute_delivery_price = False
                self.update({
                    'state': 'approve_superior'
                })
