from odoo import api, fields, models, _


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def get_payment_context_flat_file(self):
        context = {
            'default_partner_id': self.partner_id.id,
            'default_bank_id': self.journal_id.bank_account_id.bank_id.id,
            'default_account_debit': (
                self.journal_id.bank_account_id.acc_number),
            'default_account_type': self.journal_id.bank_account_id.acc_type,
            'default_file_extension': "txt",
            'default_file_type': "get_collect_data_bank",
            'payment_name': self.name,
            'payment_type': 'Payment'
        }
        return context

    def generate_flat_file(self):
        context = self.get_payment_context_flat_file()
        return {
            'name': _("Generate Flat File"),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.flat.file.base',
            'view_id': self.env.ref(
                'account_flat_file_base.'
                'account_flat_file_base_wizard_form').id,
            'target': 'new',
            'context': context
        }
