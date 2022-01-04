# Copyright 2020 Raul Carbonell
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class ResPartnerHidePrice(models.Model):
    _inherit = "res.partner"

    is_hide_price_web = fields.Boolean(string="Ocultar Precio Web", )
