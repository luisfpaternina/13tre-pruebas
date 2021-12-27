import re
from odoo import fields, api, models, _


class AccountAccount(models.Model):
    _inherit = 'account.account'

    allows_accounting_closing = fields.Boolean(
        string=_('Allows accounting closing'), readonly=True)

    @api.onchange('code')
    def _onchange_code(self):
        if self.code:
            code = self.code
            self.allows_accounting_closing = self._get_pattern(code)

    @api.model
    def create(self, values):
        code = values.get('code', False)
        if code:
            values['allows_accounting_closing'] = self._get_pattern(code)

        return super(AccountAccount, self).create(values)

    def write(self, values):
        code = values.get('code')
        if code:
            values['allows_accounting_closing'] = self._get_pattern(code)

        return super(AccountAccount, self).write(values)

    def _get_pattern(self, code):
        pattern = bool(re.match('^[4|5|6|7]', code))
        if pattern:
            return True
        else:
            return False
