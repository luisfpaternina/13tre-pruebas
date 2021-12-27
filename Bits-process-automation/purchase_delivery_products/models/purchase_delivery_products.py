# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class PurchaseDeliveryProducts(models.Model):
    _inherit = "purchase.order"
    _description = _("Check Delivery")

    delivered_products = fields.Boolean(
        string=_('Delivered products ?'),
        compute='_compute_delivered_products')

    # Settear en True el Campo productos recibidos
    # (Cuando se marca el recibo de recepción en terminado) Modulo de Stock.
    @api.depends('picking_ids', 'picking_ids.state')
    def _compute_delivered_products(self):
        for order in self:
            if order.picking_ids and any([x.state == 'done'
                                          for x in order.picking_ids]):
                order.delivered_products = True
            else:
                order.delivered_products = False

    def get_restrict_action_purchase(self, action_name):
        restrict_actions = self.env['ir.actions.restrict'].search(
            [('model', '=', self._name), ('action_name', '=', action_name)])
        if restrict_actions:
            restrict_actions.validate_user_groups()

    def action_view_invoice(self):
        self.get_restrict_action_purchase('action_view_invoice')
        return super(PurchaseDeliveryProducts, self).action_view_invoice()
