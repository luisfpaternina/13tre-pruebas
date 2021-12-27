from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import re


class HrContract(models.Model):
    _inherit = 'hr.contract'

    high_risk_pension = fields.Boolean('Hihg risk pension', default=False)
