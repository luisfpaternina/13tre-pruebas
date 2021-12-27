# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    min_gross_margin = fields.Float(
        string="Minimum Gross Margin(%)",
        related="company_id.min_gross_margin",
        readonly=False
    )


class ResCompany(models.Model):
    _inherit = 'res.company'

    min_gross_margin = fields.Float(
        string="Minimum Gross Margin(%)"
    )
