import csv
import base64
from io import BytesIO
from odoo import api, fields, models, _


class AccountFlatFileBase(models.TransientModel):
    _name = 'account.flat.file.base'

    bank_id = fields.Many2one('res.bank', 'Bank')
    bank_bic = fields.Char(related="bank_id.bic")
    partner_id = fields.Many2one('res.partner', 'Partner')
    account_debit = fields.Char('Account Debit')
    account_type = fields.Selection(
        string='Account Type',
        selection=[
            ('bank', 'Normal'),
            ('current_account', 'Current'),
            ('saving', 'Saving')
        ])
    payment_description = fields.Char('Payment Description')
    create_date = fields.Date('Create Date', default=fields.Date.context_today)
    application_date = fields.Date('Application Date')
    transaction_type = fields.Selection(
        string="Transaction Type",
        selection=[('electronic_transaction', 'Electronic Transaction')])
    file_filename = fields.Char('File Names')
    file_binary = fields.Binary(string='File')
    file_extension = fields.Selection(
        string='File Extension',
        selection=[('txt', 'TXT')]
    )

    file_type = fields.Selection([
        ('get_collect_data_bank', 'Bank')
    ], string="File Type", dafault="get_collect_data_bank")

    def get_collect_data_bank(self):
        return b'Information File'

    def get_collect_data(self):
        self_method = getattr(
            self, '%s' % (self.file_type))
        get_data = self_method()
        return get_data

    def get_data_flat_file(self):
        collect_data = self.get_collect_data()
        file_output = BytesIO(collect_data)
        file_output.seek(0)
        return file_output.read()

    def export_flat_file(self):
        get_data = self.get_data_flat_file()
        context = self.env.context
        self.write({
            'file_filename': 'flat_file.{0}'.format(self.file_extension),
            'file_binary': base64.b64encode(get_data)
        })
        return {
            'context': self.env.context,
            'name': _("Generate Flat File"),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.flat.file.base',
            'res_id': self.id,
            'view_id': self.env.ref('account_flat_file_base.'
                                    'account_flat_file_base_wizard_form').id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
