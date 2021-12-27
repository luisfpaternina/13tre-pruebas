from odoo import api, fields, models, _


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    @api.model
    def _get_supported_account_types(self):
        list_type = super(ResPartnerBank, self)._get_supported_account_types()
        list_type.append(('saving', _('Saving')))
        list_type.append(('current_account', _('Current')))
        list_type.append(('dp', _('Daviplata')))
        return list_type

    account_type = fields.Selection(
        selection=lambda x: x.env[
            'res.partner.bank'].get_supported_account_types())

    @api.depends('acc_number', 'account_type')
    def _compute_acc_type(self):
        for bank in self:
            bank.acc_type = self.retrieve_acc_type(bank.acc_number)

    @api.model
    def retrieve_acc_type(self, acc_number):
        type_retrieve = super(ResPartnerBank, self).retrieve_acc_type(
            acc_number)
        type_retrieve = (self.account_type
                         if self.account_type else type_retrieve)
        return type_retrieve
