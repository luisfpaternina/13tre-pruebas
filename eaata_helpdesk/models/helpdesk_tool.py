# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HelpdeskToolBrand(models.Model):
    _name = 'helpdesk.tool.brand'
    _description = 'Brand of tool'
    _order = 'name asc'

    name = fields.Char('Name', required=True)
    year_ids = fields.Many2many('helpdesk.year', 'helpdesk_year_tool_brand_rel', string='Years')
    active = fields.Boolean("Active", default=True)

    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)', 'Tool brand already exists.'),
    ]


class HelpdeskToolModel(models.Model):
    _name = 'helpdesk.tool.model'
    _description = 'Model of tool'
    _order = 'name asc'

    name = fields.Char('Name', required=True)
    tool_brand_id = fields.Many2one('helpdesk.tool.brand', 'Tool brand', required=True)
    service_vehicle_ids = fields.One2many('helpdesk.tool.service.vehicle', 'tool_model_id', string="Services and vehicles")
    active = fields.Boolean("Active", default=True)

    _sql_constraints = [
        ('name_uniq', 'UNIQUE (tool_brand_id, name)', 'Tool model already exists.'),
    ]

class HelpdeskToolServiceVehicle(models.Model):
    _name = 'helpdesk.tool.service.vehicle'

    tool_model_id = fields.Many2one('helpdesk.tool.model', 'Tool model', required=True)
    product_id = fields.Many2one('product.product', 'Service', required=True, domain="[('type','=', 'service')]")
    vehicle_brand_ids = fields.Many2many('helpdesk.vehicle.brand',
                                         'helpdesk_tool_service_vehicle_helpdesk_vehicle_brand_rel',
                                         'tool_service_vehicle_id',
                                         'vehicle_brand_id', string='Vehicle brands', required=True)