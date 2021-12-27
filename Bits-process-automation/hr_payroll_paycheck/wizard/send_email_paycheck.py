# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons.mail.wizard.mail_compose_message import _reopen
from odoo.exceptions import UserError
from odoo.tools.misc import get_lang


class sendPaycheck(models.TransientModel):
    _name = "send.email.paycheck"
    _inherits = {'mail.compose.message': 'composer_id'}
    _description = 'Salary Slip Send'

    is_email = fields.Boolean('Email', default=True)
    is_print = fields.Boolean('Print', default=True)
    printed = fields.Boolean('Is Printed', default=False)
    payslip_ids = fields.Many2many(
        'hr.payslip',
        'hr_payslip_paycheck_send_rel',
        string='Payslips',
        invisible=True)
    composer_id = fields.Many2one(
        'mail.compose.message',
        string='Composer',
        required=True,
        ondelete='cascade')
    template_id = fields.Many2one(
        'mail.template',
        'Use template',
        domain=[('model_id', '=', 'hr.payslip')],
        index=True
    )

    @api.model
    def default_get(self, fields):
        res = super(sendPaycheck, self).default_get(fields)
        res_ids = self._context.get('active_ids')
        mode = 'comment' if len(res_ids) == 1 else 'mass_mail'
        composer = self.env['mail.compose.message'].create({
            'composition_mode': mode
        })
        res.update({
            'payslip_ids': res_ids,
            'composer_id': composer.id,
        })
        return res

    @api.onchange('payslip_ids')
    def _compute_composition_mode(self):
        self.ensure_one()
        mode = 'comment' if len(self.payslip_ids) == 1 else 'mass_mail'
        self.composer_id.composition_mode = mode

    @api.onchange('template_id')
    def onchange_template_id(self):
        self.ensure_one()
        if self.composer_id:
            self.composer_id.template_id = self.template_id.id
            self.composer_id.onchange_template_id_wrapper()

    @api.onchange('is_email')
    def onchange_is_email(self):
        if self.is_email:
            if not self.composer_id:
                res_ids = self._context.get('active_ids')
                mode = 'comment' if len(res_ids) == 1 else 'mass_mail'
                self.composer_id = self.env['mail.compose.message'].create({
                    'composition_mode': mode,
                    'template_id': self.template_id.id
                })
            self.composer_id.onchange_template_id_wrapper()

    def _print_document(self):
        self.ensure_one()
        action = self.payslip_ids.action_payslip_print()
        action.update({'close_on_report_download': True})
        return action

    def _send_email(self):
        if self.is_email:
            self.composer_id.send_mail()

    def send_and_print_action(self):
        self.ensure_one()
        if self.composition_mode == 'mass_mail' and self.template_id:
            active_ids = self.env.context.get('active_ids', self.res_id)
            active_records = self.env[self.model].browse(active_ids)
            langs = active_records.mapped('employee_id.address_home_id.lang')
            default_lang = get_lang(self.env)
            for lang in (set(langs) or [default_lang]):
                active_ids_lang = active_records.filtered(
                    lambda r: r.employee_id.address_home_id.lang == lang).ids
                self_lang = self.with_context(
                    active_ids=active_ids_lang, lang=lang)
                self_lang.onchange_template_id()
                self_lang._send_email()
        else:
            self._send_email()
        if self.is_print:
            return self._print_document()
        return {'type': 'ir.actions.act_window_close'}
