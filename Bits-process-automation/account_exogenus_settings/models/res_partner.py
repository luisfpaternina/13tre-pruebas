# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    town_code = fields.Char(
        string="Town code",
        related="town_id.l10n_co_dian_code",
        store=True)
    state_code = fields.Char(
        string="State code",
        related="state_id.l10n_co_divipola",
        store=True)
    country_code = fields.Char(
        string="Country code",
        related="country_id.l10n_co_dian_code",
        store=True)
    bool_exclusion = fields.Boolean(
        string="Exclusion",
        store=True)
