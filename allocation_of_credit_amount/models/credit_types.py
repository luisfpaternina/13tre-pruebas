# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class CreditType(models.Model):

    _name = 'credit.type'
    _description = 'Model for management of credit types'

    name = fields.Char(
        required=True
    )
    code = fields.Char(
        copy=False,
        index=True,
        required=True
    )
    description = fields.Char()
    supporting_entity_ids = fields.Many2many(
        'res.bank', 'credit_type_supporting_entity_rel',
        'credit_type_id', 'supporting_entity_id',
        index=True
    )
    invoicing = fields.Selection(
        [
            ('client', 'On behalf of the client'),
            ('bank', 'On behalf of the financial institution')
        ],
        default='client',
        required=True
    )
    receivable = fields.Selection(
        [
            ('client', 'On behalf of the client'),
            ('bank', 'On behalf of the financial institution')
        ],
        default='client',
        required=True
    )
