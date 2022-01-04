# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

import string
import random


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # call_token_partner = fields.Char(
    #     string="RingOver Token",
    #     required=False
    # )
