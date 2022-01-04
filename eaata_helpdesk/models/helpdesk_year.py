# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HelpdeskYear(models.Model):
    _name = 'helpdesk.year'
    _description = 'Year'
    _order = 'name asc'

    name = fields.Char('Name', required=True)
    tool_brand_ids = fields.Many2many('helpdesk.tool.brand', 'helpdesk_year_tool_brand_rel', string='Brand of tools')
    product_ids = fields.Many2many('product.product', 'helpdesk_year_service_rel', string='Services')
    active = fields.Boolean("Active", default=True)
