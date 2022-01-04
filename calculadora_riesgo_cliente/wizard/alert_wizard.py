# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AlertWizard(models.TransientModel):
    _name = 'alert.wizard'
    _description = "Wizard de control de crédito"

    alerta_credito_excedido = fields.Char(
        string='Alerta Crédito Excedido',
        required=False)

    @api.model
    def default_get(self, default_fields):
        result = super(AlertWizard, self).default_get(default_fields)
        result['alerta_credito_excedido'] = "Este cliente ha superado el limite de riesgo concedido."
        return result
