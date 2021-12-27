# coding: utf-8
from odoo import fields, models


class AccountSurchangeDiscountType(models.Model):
    _name = 'surchange.discount.type'
    _description = ''

    code = fields.Char(string="Code")
    name = fields.Char(string="Type Option")

    qualifier = fields.Selection([
        ('surcharge', 'Surcharge'),
        ('discount', 'Discount')],
        required=True,
        default='surcharge'
    )
