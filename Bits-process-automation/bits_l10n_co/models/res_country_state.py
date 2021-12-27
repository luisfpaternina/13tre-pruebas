# coding: utf-8

from odoo import fields, models


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    l10n_co_divipola = fields.Char(
        "Divipola Code"
    )
