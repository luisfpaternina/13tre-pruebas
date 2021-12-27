# -*- coding: utf-8 -*-

from datetime import date
from ast import literal_eval

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    def _get_domain(self):
        return [('struct_id.type_id', '!=', False),
                ('struct_id.type_id.is_novelty', '=', True)]

    vst_rule_ids = fields.Many2many(
        'hr.salary.rule',
        'vst_rule_ids_table',
        domain=_get_domain,
    )

    avp_rule_ids = fields.Many2many(
        'hr.salary.rule',
        'avp_rule_ids_table',
        domain=_get_domain,
    )

    sln_rule_ids = fields.Many2many(
        'hr.salary.rule',
        'sln_rule_ids_table',
        domain=_get_domain,
    )
    ige_rule_ids = fields.Many2many(
        'hr.salary.rule',
        'ige_rule_ids_table',
        domain=_get_domain,
    )

    lma_rule_ids = fields.Many2many(
        'hr.salary.rule',
        'lma_rule_ids_table',
        domain=_get_domain,
    )

    vac_lr_rule_ids = fields.Many2many(
        'hr.salary.rule',
        'vac_lr_rule_ids_table',
        domain=_get_domain,
    )

    irl_rule_ids = fields.Many2many(
        'hr.salary.rule',
        'irl_rule_ids_table',
        domain=_get_domain,
    )

    integral_salary_structure_ids = fields.Many2many(
        'hr.payroll.structure',
        'hr_payroll_structure_id_ids_table',
    )

    sena_salary_structure_ids = fields.Many2many(
        'hr.payroll.structure',
        'sena_salary_structure_ids_table',
    )

    entity_arl = fields.Many2one(
        'social.security',
        config_parameter='hr_payroll.entity_arl_id',
        domain="[('entity_type', '=', 'arl')]",
    )

    rate_subsistence_afs = fields.Float(
        config_parameter='hr_payroll.rate_subsistence_afs',
        default=50.0)
    rate_solidarity_afs = fields.Float(
        config_parameter='hr_payroll.rate_solidarity_afs',
        default=50.0)

    ibc_adjustment_rule_ids = fields.Many2many(
        'hr.salary.rule',
        'ibc_adjustment_rule_ids_table',
        domain=_get_domain,
    )

    non_apply_box_rule_ids = fields.Many2many(
        'hr.salary.rule',
        'non_apply_box_rule_ids_table',
        domain=_get_domain,
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        with_user = self.env['ir.config_parameter'].sudo()
        rules = [
            'vst_rule_ids', 'avp_rule_ids', 'sln_rule_ids',
            'ige_rule_ids', 'lma_rule_ids', 'vac_lr_rule_ids',
            'irl_rule_ids', 'integral_salary_structure_ids',
            'ibc_adjustment_rule_ids', 'non_apply_box_rule_ids',
            'sena_salary_structure_ids',
        ]
        for rule in rules:
            rule_id = with_user.get_param('many2many.' + rule)
            res[rule] = [(6, 0, literal_eval(rule_id))] \
                if rule_id else False
        return res

    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.vst_rule_ids', self.vst_rule_ids.ids)
        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.avp_rule_ids', self.avp_rule_ids.ids)
        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.sln_rule_ids', self.sln_rule_ids.ids)
        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.ige_rule_ids', self.ige_rule_ids.ids)
        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.lma_rule_ids', self.lma_rule_ids.ids)
        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.vac_lr_rule_ids', self.vac_lr_rule_ids.ids)
        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.irl_rule_ids', self.irl_rule_ids.ids)
        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.integral_salary_structure_ids',
            self.integral_salary_structure_ids.ids)
        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.ibc_adjustment_rule_ids',
            self.ibc_adjustment_rule_ids.ids)
        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.non_apply_box_rule_ids',
            self.non_apply_box_rule_ids.ids)
        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.sena_salary_structure_ids',
            self.sena_salary_structure_ids.ids)
        return res
