# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class Bank(models.Model):
    _inherit = 'res.bank'

    partner_id = fields.Many2one('res.partner')
