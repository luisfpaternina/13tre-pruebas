from odoo import models, fields, api, _


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def get_mail_values(self, res_ids):
        send_payroll = self.env['send.email.payroll.approval'].search(
            [
                ('composer_id', '=', self.id)
            ]
        )
        result = super(MailComposeMessage, self).get_mail_values(res_ids)
        res_id = res_ids[0]
        partners = self.env['hr.payslip'].search(
            [
                ('id', '=', res_id)
            ]
        ).search_financial_administrative_director()[0]
        if (
            self.env.context.get("send_mass")
            and
            self.composition_mode == 'mass_mail'
        ):
            result = {res_id: result[res_id]}
            result[res_id]['attachment_ids'].pop()
            result[res_id]['attachment_ids'].append(
                send_payroll.action_generate_attachment())
            result[res_id]['recipient_ids'] += partners.ids
        return result
