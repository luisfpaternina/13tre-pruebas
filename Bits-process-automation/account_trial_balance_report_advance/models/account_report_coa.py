# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from copy import deepcopy
from odoo import models, api, _, fields
import logging
_logger = logging.getLogger(__name__)


class AccountChartOfAccountReport(models.AbstractModel):
    _inherit = "account.coa.report"

    filter_levels_niff = True
    filter_levels_filter = None
    filter_range_account = True
    filter_levels = False

    @api.model
    def _init_filter_range_account(self, options, previous_options=None):
        if self.filter_range_account is None:
            return
        # Account_accounts
        model_account = "account.account"
        options['range_account'] = self.filter_range_account
        options['account_accounts'] = (
            previous_options and previous_options.get(
                'account_accounts') or [])
        account_accounts_ids = options['account_accounts']
        selected_account_accounts = (
            account_accounts_ids
            and self.env[model_account
                         ].browse(account_accounts_ids)
            or self.env[model_account])
        options['selected_account_account_names'] = (
            selected_account_accounts.mapped('name'))
        # Account_accounts_to
        options['account_accounts_to'] = (
            previous_options and previous_options.get(
                'account_accounts_to') or [])
        account_to_ids = options['account_accounts_to']
        selected_account_accounts_to = (
            account_to_ids
            and self.env[model_account
                         ].browse(account_to_ids)
            or self.env[model_account])
        options['selected_account_account_names_to'] = (
            selected_account_accounts_to.mapped('name'))
