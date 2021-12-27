# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    town_id = fields.Many2one('res.country.town', string="Ciudad")
    agent_id = fields.Many2one('res.partner', string="Representante legal")