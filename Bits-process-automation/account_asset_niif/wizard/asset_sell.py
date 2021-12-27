# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AssetSell(models.TransientModel):
    _inherit = 'account.asset.sell'

    loss_account_colgap_id = fields.Many2one(
        'account.account',
        string=_("Lost Account COLGAP"),
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]",
        related='company_id.loss_account_colgap_id',
        help="Account used to write the journal item in case of loss," +
             " COLGAP accounting",
        readonly=False)
