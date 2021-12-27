# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, SUPERUSER_ID, _


class PosConfig(models.Model):
    _inherit = "pos.config"

    street = fields.Char()
