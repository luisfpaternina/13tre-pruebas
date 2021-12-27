# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ReasonsForTermination(models.Model):
    _name = 'reasons.for.termination'

    code = fields.Char(required=True, unique=True)
    name = fields.Char(required=True)
    salary_structure = fields.Many2one(
        'hr.payroll.structure',
        string="Salary structure",
        required=True,
        domain="[('type_id', '=', 'Liquidación')]"
    )
