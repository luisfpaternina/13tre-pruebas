# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import json


class sale_list_price_validation(models.Model):
    _inherit = "product.pricelist.item"

    @api.constrains(
        'fixed_price',
        'applied_on',
        'compute_price',
        'categ_id',
        'product_tmpl_id',
        'product_id'
    )
    def list_price_validation(self):
        for record in self:
            if record.compute_price != 'fixed':
                continue
            if record.applied_on != '0_product_variant'\
                                    and record.applied_on != '3_global':
                products = self.env['product.template'].search(
                    [
                        ('categ_id', '=', record.categ_id.id)
                        if record.applied_on == '2_product_category'
                        else (
                            ('id', '=', record.product_tmpl_id.id)
                            if record.applied_on == '1_product'
                            else (
                            )
                        )
                    ]
                )
            elif record.applied_on == '0_product_variant':
                products = self.env['product.product'].search(
                    [
                        ('id', '=', record.product_id.id)
                    ]
                )
            else:
                products = self.env['product.template'].search([])

            products_rejected = []
            for product in products:
                if record.fixed_price < product.standard_price:
                    products_rejected.append(product)
            if len(products_rejected) != 0:
                dict_products_rejected = {}
                for pr in products_rejected:
                    dict_products_rejected[pr.id] = pr.default_code
                message = ""
                for product in dict_products_rejected.values():
                    message += f'{product}, '
                raise ValidationError(_('%s for these products '
                                        'the cost is higher than the '
                                        'price of the product.') % (message))
