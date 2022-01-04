# -*- coding: utf-8 -*-

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    support_active = fields.Boolean("Support active", default=True)
    tool_ids = fields.One2many('res.partner.tool', 'partner_id', string="Tools")


class ResPartnerTool(models.Model):
    _name = 'res.partner.tool'

    name = fields.Char('Serial Number', required=True)
    tool_brand_id = fields.Many2one('helpdesk.tool.brand', 'Tool brand', required=True)
    tool_model_id = fields.Many2one('helpdesk.tool.model', 'Tool model', required=True,
                                    domain="[('tool_brand_id', '=', tool_brand_id)]")
    partner_id = fields.Many2one('res.partner', 'Customer', required=True)
    date_from = fields.Date(string='From', readonly=True, help='Start date of support service.')
    date_to = fields.Date(string='To', readonly=True, help='End date of support service.')
    support_active = fields.Boolean("Support active", readonly=True)
    fecha_actualizacion = fields.Date(string='Fecha de Actualización')
