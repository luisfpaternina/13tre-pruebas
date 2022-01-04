# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HelpdeskVehicleBrand(models.Model):
    _name = 'helpdesk.vehicle.brand'
    _description = 'Brand of vehicle'
    _order = 'name asc'

    name = fields.Char('Name', required=True)
    service_vehicle_ids = fields.Many2many('helpdesk.tool.service.vehicle',
                                           'helpdesk_tool_service_vehicle_helpdesk_vehicle_brand_rel',
                                           'vehicle_brand_id', 'tool_service_vehicle_id',string='Services')
    active = fields.Boolean("Active", default=True)

    _sql_constraints = [
        ('name_uniq', 'UNIQUE (name)', 'Vehicle brand already exists.'),
    ]
