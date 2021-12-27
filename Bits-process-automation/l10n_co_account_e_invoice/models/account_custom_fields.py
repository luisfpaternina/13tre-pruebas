# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountCustomFields(models.Model):
    _name = 'l10n_co.custom.fields'
    _description = 'It allows adding custom fields in the electronic invoice'

    code = fields.Char(required=True)
    name = fields.Char(required=True)
    active = fields.Boolean(default=True)

    method_type = fields.Selection(
        [('note', 'Text in note field'),
         ('OR', 'Reference Order (UBL)'),
         ('NC', 'Related Credit Note (UBL)'),
         ('NC', 'Related Debit Note (UBL)'),
         ('DD', 'Dispatch Documents (UBL)'),
         ('DR', 'Receiving Documents (UBL)'),
         ('RA', 'Additional References (UBL)'),
         ('ON', 'Purchase order'),
         ('OV', 'Sale order'),
         ('CO', 'Contract'),
         ('GC', 'Contract group'),
         ('IN', 'Invoice'),
         ('RE', 'Remission'),
         ('QR', 'Delivery number')],
        string='Qualifier',
        default='note'
    )
