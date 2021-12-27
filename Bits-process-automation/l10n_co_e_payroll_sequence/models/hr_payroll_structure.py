# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HrPayrollStructureInherit(models.Model):
    _inherit = 'hr.payroll.structure'

    sequence_number_next = fields.Integer(
        string='Next number',
        related="sequence_id.number_increment"
        )

    sequence_id = fields.Many2one('ir.sequence')
