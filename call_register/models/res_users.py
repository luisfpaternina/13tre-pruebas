# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    ring_over_user_id = fields.Char(
        string="RingOver User Id",
        required=False
    )
    # ring_over_token = fields.Char(
    #     string="RingOver Api Key",
    #     required=False
    # )
