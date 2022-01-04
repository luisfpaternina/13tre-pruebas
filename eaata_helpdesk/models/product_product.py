# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    tool_vehicle_ids = fields.One2many('helpdesk.tool.service.vehicle', 'product_id', string="Models and vehicles")
    year_ids = fields.Many2many('helpdesk.year', 'helpdesk_year_service_rel', string='Years')
