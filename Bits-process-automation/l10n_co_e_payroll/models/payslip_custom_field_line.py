# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PayslipCustomFieldLine(models.Model):
    _name = 'payslip.custom.field.line'

    payslip_id = fields.Many2one(
        'hr.payslip',
        required=True
    )
    code = fields.Char()
    method_type = fields.Selection(
        [('note', 'Texto en Campo nota')],
    )
    value = fields.Char(required=True)
