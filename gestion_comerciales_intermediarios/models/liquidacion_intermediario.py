# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class LiquidacionIntermediario(models.Model):
    _name = "liquidacion.intermediario"
    _description = "Controla las liquidaciones para usuarios intermediarios"

    name = fields.Char(string="Titulo")
    intermediario_id = fields.Many2one('res.users', 'Intermediario')
    total_liquidacion = fields.Float(string="Total liquidacion intermediario")
    fecha_creacion = fields.Datetime()
    fecha_liquidado = fields.Datetime(string="")
    es_liquidado = fields.Boolean(string="Esta liquidado")

    def calcular(self):
        return ""
