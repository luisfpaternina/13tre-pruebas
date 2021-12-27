# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductCategory(models.Model):
    _inherit = 'product.category'

    apply_discount_table = fields.Boolean(
        string='Apply discount table',
        default=False
    )
