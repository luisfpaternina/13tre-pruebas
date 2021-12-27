# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class DianFiscalResponsability(models.Model):
    _name = 'dian.fiscal.responsability'
    _description = 'Model DIAN Fiscal Responsability'

    code = fields.Char(
        string="DIAN Fiscal Responsibility Code",
        required=True)
    name = fields.Char(
        string="DIAN Fiscal Responsibility Meaning",
        required=True)
    active = fields.Boolean(default=False)
    line_ids = fields.One2many(
        'dian.fiscal.responsability.line',
        'parent_id'
    )
