# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval


class HrPayrollActFields(models.Model):
    _inherit = 'account.act.fields'

    _type = fields.Selection(selection_add=[('payroll', 'Payroll')])
    active = fields.Boolean('It is active', default=True, tracking=True)
