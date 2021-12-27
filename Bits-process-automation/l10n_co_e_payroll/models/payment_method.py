from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from ast import literal_eval
from odoo import api, fields, models, _
from odoo.tools import float_round
from odoo.exceptions import UserError, ValidationError


class PaymentForm(models.Model):
    _name = 'payment.method'

    name = fields.Char(String='Means')
    code = fields.Char(string="Code")
