# Copyright 2020 Raul Carbonell
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.http import request

class WebSiteHidePrice(models.Model):
    _inherit = "website"

    is_hide_price_web = fields.Boolean(
        compute='_compute_is_hide_price_web')

    def _compute_is_hide_price_web(self):
        for rec in self:
            rec.is_hide_price_web = (request.env.user.partner_id.is_hide_price_web)
