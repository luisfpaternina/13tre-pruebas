from odoo import models, fields, api, _
from odoo.osv import expression


class AccountReconciliation(models.AbstractModel):
    _inherit = 'account.reconciliation.widget'

    def _domain_move_lines_for_reconciliation(self, st_line, aml_accounts,
                                              partner_id, excluded_ids=[],
                                              search_str=False, mode='rp'):
        domain = super(
            AccountReconciliation, self)._domain_move_lines_for_reconciliation(
                st_line, aml_accounts,
                partner_id, excluded_ids=[], search_str=False, mode='rp')
        conciliation_type = self.get_config_value(
            "conciliation_type")

        if conciliation_type == "value":
            domain = expression.AND(
                [domain, [('balance', '=', st_line.amount)]])

        return domain

    def get_config_value(self, name):
        _parameter_value = self.env['ir.config_parameter'].sudo()
        config_value = _parameter_value.get_param(
            'account_statement_conciliation.' + name)
        return config_value
