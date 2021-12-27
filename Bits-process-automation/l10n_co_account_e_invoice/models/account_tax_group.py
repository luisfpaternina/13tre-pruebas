# coding: utf-8

from odoo import api, fields, models, _


class AccountTaxGroup(models.Model):
    _inherit = 'account.tax.group'

    active = fields.Boolean(default=False)
