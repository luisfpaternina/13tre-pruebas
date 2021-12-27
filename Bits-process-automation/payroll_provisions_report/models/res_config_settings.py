# -*- coding: utf-8 -*-

from datetime import date
from ast import literal_eval

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    salary_provision_rule = fields.Many2many(
        'hr.salary.rule',
        'salary_provision_rule_table',
        string='SALARY',
    )

    overtime_provision_rule = fields.Many2many(
        'hr.salary.rule',
        'overtime_provision_rule_table',
        string='COMMI + OT',
    )

    adjustment_provision_rule = fields.Many2many(
        'hr.salary.rule',
        'adjustment_provision_rule_table',
        string='ADJUSTMENT',
    )

    closing_adjustment_provision_rule = fields.Many2many(
        'hr.salary.rule',
        'closing_adjustment_provision_rule_table',
        string='CLOSING ADJUSTMENT',
    )

    bonus_provision_rule = fields.Many2many(
        'hr.salary.rule',
        'bonus_provision_rule_table',
        string='BONUS PROVISION',
    )

    provision_rule = fields.Many2many(
        'hr.salary.rule',
        'provision_rule_table',
        string='LAYOFFS PROVISION',
    )

    vacations_provision_rule = fields.Many2many(
        'hr.salary.rule',
        'vacations_provision_rule_table',
        string='VACATIONS PROVISION',
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        with_user = self.env['ir.config_parameter'].sudo()
        rules = [
            'salary_provision_rule', 'overtime_provision_rule',
            'adjustment_provision_rule', 'closing_adjustment_provision_rule',
            'bonus_provision_rule', 'provision_rule',
            'vacations_provision_rule'
        ]
        for rule in rules:
            rule_id = with_user.get_param('many2many.' + rule)
            res[rule] = [(6, 0, literal_eval(rule_id))] \
                if rule_id else False
        return res

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.salary_provision_rule',
            self.salary_provision_rule.ids)
        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.overtime_provision_rule',
            self.overtime_provision_rule.ids)
        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.adjustment_provision_rule',
            self.adjustment_provision_rule.ids)
        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.closing_adjustment_provision_rule',
            self.closing_adjustment_provision_rule.ids)
        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.bonus_provision_rule',
            self.bonus_provision_rule.ids)
        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.provision_rule',
            self.provision_rule.ids)
        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.vacations_provision_rule',
            self.vacations_provision_rule.ids)
        return res
