# coding: utf-8

from odoo import fields, models


class ResCountryTown(models.Model):
    _name = 'res.country.town'
    _description = "Municipalities of the country"
    # _order = 'code'

    code = fields.Char(required=True)
    name = fields.Char(required=True)
    country_id = fields.Many2one(
        'res.country',
        string='Country',
        required=True
    )
    state_id = fields.Many2one(
        'res.country.state',
        string='State',
        domain="[('country_id', '=', country_id)]",
        required=True
    )
    l10n_co_divipola = fields.Char(
        "Divipola Code"
    )
    l10n_co_dian_code = fields.Char(
        "Dian Code"
    )
