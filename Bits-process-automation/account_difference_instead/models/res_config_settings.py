# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    unrealized_exchange_vendors = fields.Many2one(
        "account.account",
        string=_("Vendors - Unrealized exchange rate difference"),
        config_parameter=("account_difference_instead."
                          "unrealized_exchange_vendors")
    )

    unrealized_exchange_expenses = fields.Many2one(
        "account.account",
        string=_("Vendors - Expenses - Unrealized exchange rate difference"),
        config_parameter=("account_difference_instead."
                          "unrealized_exchange_expenses")
    )

    unrealized_exchange_income = fields.Many2one(
        "account.account",
        string=_("Vendors - Income - Unrealized exchange rate difference"),
        config_parameter=("account_difference_instead."
                          "unrealized_exchange_income")
    )

    unrealized_exchange_journal = fields.Many2one(
        "account.journal",
        string=_("Vendors - Journal - Unrealized exchange rate difference"),
        config_parameter=("account_difference_instead."
                          "unrealized_exchange_journal")
    )

    unrealized_exchange_customers = fields.Many2one(
        "account.account",
        string=_("Customers - Unrealized exchange rate difference"),
        config_parameter=("account_difference_instead."
                          "unrealized_exchange_customers")
    )
