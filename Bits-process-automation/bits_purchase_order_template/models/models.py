# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PurchaseOrderTemplate(models.Model):
    _inherit = 'purchase.order'
    _description = ''

    def action_rfq_send(self):
        res = super(PurchaseOrderTemplate, self).action_rfq_send()
        if not self.env.context.get('send_rfq', True):
            template = self.env.ref(
                'bits_purchase_order_template.'
                'email_template_custom_purchase_done',
                False
            )
            res['context'].update({
                'default_template_id': template.id,
            })
        return res
