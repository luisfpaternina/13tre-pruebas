# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    city = fields.Char(
        string='City', related='town_id.name'
    )
