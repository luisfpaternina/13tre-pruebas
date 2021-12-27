# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    salary_rule_account_ids = fields.One2many(
        'hr.salary.rule.account', 'salary_rule_id', string='Accounts')
    search_parafiscales = fields.Boolean(string="Search Parafiscales")
    applies_all_cost_center = fields.Boolean(string="Search Cost Center")
    import_code = fields.Char(string=_('Import Code'))
