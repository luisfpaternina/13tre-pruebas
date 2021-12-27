# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import date
# import numpy_financial as npf


class AccountMove(models.Model):
    _inherit = "account.move"

    credit_line_id = fields.Many2one(
        comodel_name='credit.line',
        string='Credit Line'
    )
    