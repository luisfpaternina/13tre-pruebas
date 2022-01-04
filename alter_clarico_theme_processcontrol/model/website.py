# -*- coding: utf-8 -*-

import json

import werkzeug.urls
import werkzeug.utils
from odoo.http import request
from odoo.tools import image_process

import odoo
from odoo import fields, models, http, exceptions
from odoo.addons.auth_oauth.controllers.main import OAuthLogin


class Website(models.Model):
    _inherit = "website"

    def get_multibrand(self):
        shop_brands = self.env['marcas'].sudo().search([])
        return shop_brands
