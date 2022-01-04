# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AlertDebtWizard(models.TransientModel):
    _name = 'alert.debt.wizard'
    _description = "Wizard de impagos"

    alerta_impago = fields.Char(
        string='Alerta Impago',
        required=False)

    @api.model
    def default_get(self, default_fields):
        result = super(AlertDebtWizard, self).default_get(default_fields)
        if self._context.get('invoices_with_debt') != "":
            result['alerta_impago'] = "Este cliente tiene impagos en las siguientes facturas: " + self._context.get(
                'invoices_with_debt')
        return result
