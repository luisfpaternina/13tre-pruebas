# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class AccountExtraRefs(models.Model):
    _name = 'account.extra.refs'
    _description = ''

    custom_field_id = fields.Many2one(
        'l10n_co.custom.fields',
    )
    parent_id = fields.Many2one(
        'account.move',
    )
    value = fields.Char()
