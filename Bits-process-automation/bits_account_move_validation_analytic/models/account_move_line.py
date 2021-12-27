from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    _description = "Journal Item"

    @api.constrains('analytic_account_id', 'account_id')
    def _check_analytic_account_id_required(self):
        user_type_ids = self.env['ir.config_parameter'].sudo()\
            .get_param('many2many.user_type_ids')
        for line in self:
            if not line.account_id.user_type_id or not user_type_ids:
                continue
            if str(line.account_id.user_type_id.id) in user_type_ids \
               and not line.analytic_account_id:
                raise ValidationError(
                    _('The analytical account must be required for this '
                      'type of account.')
                )
