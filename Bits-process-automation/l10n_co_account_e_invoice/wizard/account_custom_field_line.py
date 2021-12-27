# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountCustomFieldLine(models.TransientModel):
    _name = 'wizard.custom.field.line'
    _description = 'It allows adding custom fields in the electronic invoice'

    custom_field_id = fields.Many2one(
        'l10n_co.custom.fields',
        required=True
    )
    parent_id = fields.Many2one(
        'support.files.send',
        required=True
    )
    code = fields.Char(related='custom_field_id.code')
    method_type = fields.Selection(
        [('note', 'Texto en Campo nota'),
         ('OR', 'Orden de Referencia (UBL)'),
         ('NC', 'Nota de Crédito Relacionada (UBL)'),
         ('NC', 'Nota de Débito Relacionada (UBL)'),
         ('DD', 'Documentos de Despacho (UBL)'),
         ('DR', 'Documentos de Recepción (UBL)'),
         ('RA', 'Referencias Adiconales (UBL)'),
         ('ON', 'Orden de Compra'),
         ('OV', 'Orden de Venta'),
         ('CO', 'Contrato'),
         ('GC', 'Grupo de Contrato'),
         ('IN', 'Factura'),
         ('RE', 'Remisión'),
         ('QR', 'Numero entrega')],
        related='custom_field_id.method_type'
    )
    value = fields.Char(required=True)
