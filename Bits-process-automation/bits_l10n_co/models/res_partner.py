# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    town_id = fields.Many2one(
        'res.country.town',
        string=_('Town'),
        domain="[('state_id', '=', state_id)]",
    )

    divipola_town = fields.Char(
        related='town_id.l10n_co_divipola',
        readonly=True
    )

    divipola_state = fields.Char(
        related='state_id.l10n_co_divipola',
        readonly=True
    )

    l10n_co_dian_code = fields.Char(
        related='country_id.l10n_co_dian_code'
    )
