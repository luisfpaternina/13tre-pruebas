from odoo import models, fields, api, _
from ast import literal_eval


class AccountBankStatementConciliationSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    conciliation_type = fields.Selection(
        [
            ('value', 'Reconcile by value'),
            ('standard', 'Reconcile standard')
        ],
        config_parameter=("account_statement_conciliation."
                          "conciliation_type")
    )
