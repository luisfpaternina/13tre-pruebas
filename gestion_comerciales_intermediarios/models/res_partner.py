# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = ['res.partner']

    intermediario_id = fields.Many2one('res.users', 'Intermediario')
    porcentaje_intermediario = fields.Float(string="Porcentaje de comision al intermediario")
