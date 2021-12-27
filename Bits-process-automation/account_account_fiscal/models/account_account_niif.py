# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.modules.module import get_module_resource


class AccountAccountNiif(models.Model):
    _inherit = 'account.account'

    fiscal = fields.Boolean(
        string="Affects fiscal accounting"
    )
    homologation_account_fiscal_id = fields.Many2one(
        "account.account",
        domain="[('fiscal', '=', True)]",
        string="Fiscal homologated account"
    )
    use_homologation = fields.Boolean(
        related="company_id.use_account_homologation"
    )

    @api.onchange('fiscal')
    def _onchange_homologation_fiscal(self):
        self.homologation_account_fiscal_id = (
            False if self.homologation_account_fiscal_id else False)
