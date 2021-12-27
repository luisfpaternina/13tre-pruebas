# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class TechProviderSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    provider_payroll_id = fields.Many2one(
        'l10n_co.tech.provider',
        readonly=False,
        string="Enabled provider",
        config_parameter="l10n_co_tech_provider_payroll.provider_payroll_id"
    )

    user_payroll_provider = fields.Char(
        string="User",
        related="provider_payroll_id.username",
        readonly=False
    )

    password_payroll_provider = fields.Char(
        string="Password",
        related="provider_payroll_id.password",
        readonly=False
    )

    is_payroll_test = fields.Boolean(
        string="Test mode",
        related="provider_payroll_id.is_test",
        default=True,
        readonly=False
    )
