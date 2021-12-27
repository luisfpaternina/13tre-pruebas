from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging


class AccountAccount(models.Model):
    _inherit = 'account.account'

    is_refund = fields.Boolean(string="Is a refund")
    lower_amount = fields.Float(string="Lower amount")
