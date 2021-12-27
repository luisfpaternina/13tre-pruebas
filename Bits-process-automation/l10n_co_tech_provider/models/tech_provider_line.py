# -*- coding: utf-8 -*-

import csv
import base64
from io import BytesIO
from odoo import models, fields, api


class TechProviderLine(models.Model):
    _name = 'l10n_co.tech.provider.line'
    _order = "sequence"
    _parent_store = True

    name = fields.Char('Section Name', translate=True)
    code = fields.Char('Code')
    description = fields.Text()
    tech_provider_id = fields.Many2one(
        'l10n_co.tech.provider',
        'Financial Report')
    parent_id = fields.Many2one(
        'l10n_co.tech.provider.line',
        string='Parent',
        ondelete='cascade')
    children_ids = fields.One2many(
        'l10n_co.tech.provider.line',
        'parent_id',
        string='Children')
    parent_path = fields.Char(index=True)
    sequence = fields.Integer()

    level = fields.Integer(required=True)

    act_field_id = fields.Many2one(
        'account.act.fields',
        string='Related field'
    )
