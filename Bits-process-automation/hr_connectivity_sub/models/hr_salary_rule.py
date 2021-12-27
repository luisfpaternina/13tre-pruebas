# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    amount_fix = fields.Float(
        compute='_compute_amount_fix',
        inverse='inverse_amount_fix',
        store=True,
        defaul=0.0,
    )

    def inverse_amount_fix(self):
        for record in self:
            record.amount_fix = record.amount_fix