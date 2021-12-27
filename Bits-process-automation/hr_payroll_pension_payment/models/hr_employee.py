# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrPayrollPensionPayment(models.Model):

    _inherit = 'hr.employee'

    pensions_contrib = fields.Boolean(
        default=False,
        string="Not Obliged Contribute Pension",
        help="Person not obliged to contribute pensions")
