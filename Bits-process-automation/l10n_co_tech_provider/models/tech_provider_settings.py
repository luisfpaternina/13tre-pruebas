# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class TechProviderSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    provider_id = fields.Many2one(
        'l10n_co.tech.provider',
        readonly=False,
        string="Enabled provider",
        config_parameter="l10n_co_tech_provider.provider_id"
    )

    user_provider = fields.Char(
        string="User",
        related="provider_id.username",
        readonly=False
    )

    password_provider = fields.Char(
        string="Password",
        related="provider_id.password",
        readonly=False
    )

    is_test = fields.Boolean(
        string="Test mode",
        related="provider_id.is_test",
        default=True,
        readonly=False
    )
