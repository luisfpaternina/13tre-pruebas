# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountJournalNiif(models.Model):

    _inherit = "account.journal"

    accounting = fields.Selection(
        [
            ("niif", "NIIF"),
            ("fiscal", "Fiscal"),
            ("both", "Both")
        ],
        string="Accounting"
    )
