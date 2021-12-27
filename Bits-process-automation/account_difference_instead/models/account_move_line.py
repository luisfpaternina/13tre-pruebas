# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.modules.module import get_module_resource


class AccountDifferenceInstead(models.Model):
    _inherit = 'account.move.line'

    bill_id = fields.Many2one(
        "account.move",
        string="Bill related"
    )
