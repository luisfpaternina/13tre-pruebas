# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountTax(models.Model):
    _inherit = 'account.tax'

    is_rtefte = fields.Boolean(string="Is rtefte")
    is_rteiva = fields.Boolean(string="Is rteIVA")
    is_exterior = fields.Boolean(string="Is Exterior")
