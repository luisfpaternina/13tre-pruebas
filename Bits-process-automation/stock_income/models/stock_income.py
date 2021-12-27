# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.misc import get_lang


class StockIncome(models.Model):
    _name = 'stock.picking'
    _inherit = ['stock.picking', 'mail.thread', 'portal.mixin']

    def send_confirmation_of_receipt(self):
        self.ensure_one()
        template = self.env.ref(
            'stock_income.send_confirmation_suppliers_email_template',
            raise_if_not_found=False
        )
        lang = get_lang(self.env)
        if template and template.lang:
            lang = template._render_template(
                template.lang,
                'stock.picking',
                self.id
            )
        else:
            lang = lang.code
        compose_form = self.env.ref(
            'stock_income.view_wizard_send_confirmation_to_suppliers',
            raise_if_not_found=False
        )
        ctx = dict(
            default_model='stock.picking',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            custom_layout="mail.mail_notification_paynow",
            model_description=_('sent confirmation to suppliers'),
            force_email=True
        )
        return {
            'name': _('Send Confirm to Suppliers'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'send.confirmation.to.suppliers',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    def print_receipt_confirmation(self):
        return self.env.ref(
            "stock.action_report_delivery"
        ).report_action(self)
