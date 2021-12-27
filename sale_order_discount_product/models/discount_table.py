# -*- coding: utf-8 -*-

from odoo import models, fields, api


class DiscountTable(models.Model):
    _name = 'discount.table'
    _description = 'discount.table'

    min_quantity = fields.Float(
        string='Minimum Quantity'
    )

    max_quantity = fields.Float(
        string='Maximum Quantity'
    )
    min_discount = fields.Float(
        string='Minimum Discount'
    )

    max_discount = fields.Float(
        string='Maximum Discount'
    )

    name = fields.Char(
        string='Description'
    )

    code = fields.Char(
        string='Code'
    )
