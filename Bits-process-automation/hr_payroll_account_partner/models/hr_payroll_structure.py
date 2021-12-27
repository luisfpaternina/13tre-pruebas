# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    code = fields.Char(string=_('Code'))
