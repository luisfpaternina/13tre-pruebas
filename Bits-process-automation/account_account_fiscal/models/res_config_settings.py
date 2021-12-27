# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from ast import literal_eval


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    use_account_homologation = fields.Boolean(
        string=_("Use Account homologation"),
        related='company_id.use_account_homologation',
        readonly=False
    )


class ResCompany(models.Model):
    _inherit = 'res.company'

    use_account_homologation = fields.Boolean(
        string=_("Use Account homologation")
    )
