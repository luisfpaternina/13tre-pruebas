# Copyright 2020 Raul Carbonell
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class ProductTemplateHidePrice(models.Model):
    _inherit = "product.template"

    show_price_in_public_web = fields.Boolean(string="Mostrar Precio en Web Pública", )
