# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    provider_id = fields.Many2one(
        comodel_name='l10n_co.tech.provider',
        string='Enabled provider',
    )
