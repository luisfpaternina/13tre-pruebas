from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from ast import literal_eval
from odoo import api, fields, models, _
from odoo.tools import float_round
from odoo.exceptions import UserError, ValidationError


class PaymentWay(models.Model):
    _name = 'payment.way'

    name = fields.Char(String='Meaning')
    code = fields.Char(string="Code")
