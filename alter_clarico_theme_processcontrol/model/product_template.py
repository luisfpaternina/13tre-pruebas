# -*- coding: utf-8 -*-

import json

import werkzeug.urls
import werkzeug.utils
from odoo.http import request
from odoo.tools import image_process

import odoo
from odoo import fields, models, http
from odoo.addons.auth_oauth.controllers.main import OAuthLogin


class ProductTemplate(models.Model):
    _inherit = "product.template"

#     marcas_ids = fields.Many2many('marcas', help="Unión de marcas de automóvil", string="Marcas")

    marcas_ids = fields.Many2many('marcas', 'marcas_transaction_rel', 'product_variant_id', 'id',
                                       string='Marcas', copy=False)
#     marcas_ids = fields.One2many('marcas', 'id', string='Marcas')