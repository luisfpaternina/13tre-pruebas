# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.misc import get_lang


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_invoice_sent(self):
        self.ensure_one()
        res = super(AccountMove, self).action_invoice_sent()
        template = self.env.ref(
            'l10n_co_e_invoice_format.email_template_edi_invoice_fe_invoice',
            raise_if_not_found=False)
        lang = get_lang(self.env)
        if template and template.lang:
            lang = template._render_template(
                template.lang, 'account.move', self.id)
        else:
            lang = lang.code
        compose_form = self.env.ref(
            'account.account_invoice_send_wizard_form',
            raise_if_not_found=False)
        res['context'].update({
            'default_use_template': bool(template),
            'default_template_id': template and template.id or False,
            'model_description': self.with_context(lang=lang).type_name,
        })
        return res

    def _get_text_info_header(self):
        self.ensure_one()
        msg = ''
        msg += self.company_id.header_regimen_activity + "</br>"
        msg += self.company_id.header_rate + "</br>"
        msg += self.company_id.header_decree + "</br>"
        return msg

