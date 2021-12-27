# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    credit_ids = fields.One2many('credit', 'res_partner_id')
