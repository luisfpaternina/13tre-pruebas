# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons.mail.wizard.mail_compose_message import _reopen
from odoo.exceptions import UserError
from odoo.tools.misc import get_lang

import base64


class SendPayrollApproval(models.TransientModel):
    _name = "send.email.payroll.approval"
    _inherits = {'mail.compose.message': 'composer_id'}
    _description = 'Payroll Approval Send'

    is_email = fields.Boolean('Email', default=True)
    is_print = fields.Boolean('Print', default=True)
    printed = fields.Boolean('Is Printed', default=False)
    payslip_ids = fields.Many2many(
        'hr.payslip',
        'hr_payslip_approval_send_rel',
        string='Payslips',
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
        domain=[('model_id', '=', 'hr.payslip')],
        index=True
    )

    @api.onchange('payslip_ids')
    def _compute_composition_mode(self):
        self.ensure_one()
        mode = 'comment' if len(self.payslip_ids) == 1 else 'mass_mail'
        self.composer_id.composition_mode = mode

    @api.model
    def default_get(self, fields):
        res = super(SendPayrollApproval, self).default_get(fields)
        res_ids = self._context.get('active_ids')
        composer = self.env['mail.compose.message'].create({
            'composition_mode': (
                'comment' if len(res_ids) == 1 else 'mass_mail'
            ),
        })
        res.update({
            'payslip_ids': res_ids,
            'composer_id': composer.id,
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
        action = self.payslip_ids.action_payslip_custom_print()
        action.update({'close_on_report_download': True})
        return action

    def action_generate_attachment(self):
        res_ids = self._context.get('active_ids')
        report = self.env.ref(
            'hr_payroll_paycheck.hr_payroll_payslip_report',
            False
        )
        pdf_content, content_type = report.render_qweb_pdf(res_ids)
        attachment_name = 'Payrolls'
        bs4_pdf = base64.encodestring(pdf_content)
        result = self.env['ir.attachment'].create({
            'name': attachment_name,
            'type': 'binary',
            'datas': bs4_pdf,
            'store_fname': attachment_name,
            'res_model': 'hr.payslip',
            'mimetype': 'application/pdf'
        })
        return result.id

    def _send_email(self):
        if self.is_email:
            self.send_approval_with_mail()
            self.composer_id.send_mail()

    def send_approval_with_mail(self):
        self.payslip_ids.send_approval()

    def send_and_print_action(self):
        self.ensure_one()
        self._send_email()
        if self.is_print:
            return self._print_document()
        return {'type': 'ir.actions.act_window_close'}
