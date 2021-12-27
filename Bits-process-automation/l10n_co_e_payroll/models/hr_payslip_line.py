from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from ast import literal_eval
from odoo import api, fields, models, _
from odoo.tools import float_round
from odoo.exceptions import UserError, ValidationError


class PayslipLineInherit(models.Model):
    _inherit = 'hr.payslip.line'

    quantity = fields.Float(digits="Payslip Line Quantity")
    total = fields.Float(digits="Payslip Line Total")
    amount = fields.Float(digits="Payslip Line Amount")