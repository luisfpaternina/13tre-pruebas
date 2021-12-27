# coding: utf-8

from odoo import fields, models


class ResCountry(models.Model):
    _inherit = 'res.country'

    l10n_co_dian_code = fields.Char(
        "Dian Code"
    )
