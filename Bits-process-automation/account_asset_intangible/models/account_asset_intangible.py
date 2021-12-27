# -*- coding: utf-8 -*-

from odoo import models, fields, api


class account_asset_intangible(models.Model):
    _inherit = 'account.asset'

    asset_group = fields.Selection(
        [
            ('asset', 'Asset'),
            ('intangible', 'Intangible')
        ],
        default="asset",
        required=True
    )
