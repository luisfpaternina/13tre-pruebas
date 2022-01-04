# Copyright 2017 FactorLibre - Janire Olagibel
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class ProductComposition(models.Model):
    _name = "product.composition"
    _description = "Product Composition"
    _order = "default_code asc, order asc"
    _rec_name = "submaterial_id"

    product_id = fields.Many2one(
        comodel_name="product.product", string="Product", required=True
    )
    default_code = fields.Char(
        related="product_id.default_code", readonly=True, store=True
    )
    material_id = fields.Many2one(
        comodel_name="ecoembes.material", string="Material", required=True
    )
    submaterial_id = fields.Many2one(
        comodel_name="ecoembes.submaterial", string="Submaterial", required=True
    )
    packaging_id = fields.Many2one(
        comodel_name="ecoembes.packaging", string="Packaging", required=True
    )
    market_type_id = fields.Many2one(
        comodel_name="ecoembes.market.type", string="Market type", required=True
    )
    composition = fields.Boolean(string="Composition")
    weight = fields.Integer(string="Weight (g)")
    volume = fields.Integer(string="Volume (mL)")
    qty = fields.Integer(string="Qty")
    order = fields.Integer(string="Order")

    def name_get(self):
        res = []
        for item in self:
            item_name = "[{}]{}".format(
                item.product_id.default_code, item.submaterial_id.name,
            )
            res.append((item.id, item_name))
        return res
