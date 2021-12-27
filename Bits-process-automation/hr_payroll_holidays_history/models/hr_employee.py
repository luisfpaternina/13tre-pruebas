# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class HrEmployee(models.Model):
    _inherit = ['hr.employee']

    holidays_ids = fields.One2many(
        'hr.payroll.holiday.lapse',
        'employee_id',
        string='Holidays')
