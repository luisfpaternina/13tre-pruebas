# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrContract(models.Model):

    _inherit = "hr.contract"

    pensions_contrib = fields.Boolean(
        default=False,
        string="Foreigner Not Obliged Contribute Pensions",
        related="employee_id.pensions_contrib")
