# -*- coding: utf-8 -*-

import json

import werkzeug.urls
import werkzeug.utils
from odoo.http import request
from odoo.tools import image_process

import odoo
from odoo import fields, models, http
from odoo.addons.auth_oauth.controllers.main import OAuthLogin


class Marcas(models.Model):
    _name = "marcas"
    _description = 'Marcas para los productos'

    name = fields.Char(string="Nombre de la marca")
    partner_ids = fields.Many2many('res.partner', help="Unión de proveedores", string="Proveedores")
    # products_ids = fields.Many2many('product.template', help="Unión de productos", string="Productos")
