# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HelpdeskTicketType(models.Model):
    _inherit = 'helpdesk.ticket.type'

    type = fields.Selection(selection=[('assistance', 'Assistance'), ('support', 'Support')],
                            string='Internal Type')


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    name = fields.Char(string='Reference', copy=False, default=lambda self: _('New'))
    phone = fields.Char(related="partner_id.phone", readonly=1)
    ticket_type = fields.Selection(related="ticket_type_id.type", readonly=True)
    tool_brand_domain = fields.Binary(string='Tool brand domain', compute='_compute_tool_brand_domain')
    tool_brand_id = fields.Many2one('helpdesk.tool.brand', 'Tool brand', required=False)
    tool_model_domain = fields.Binary(string='Tool model domain', compute='_compute_tool_model_domain')
    tool_model_id = fields.Many2one('helpdesk.tool.model', 'Tool model', required=False,
                                    domain="[('tool_brand_id','=', tool_brand_id)]")
    product_id = fields.Many2one('product.product', 'Service', required=False,
                                 domain="[('tool_vehicle_ids.tool_model_id', '=', tool_model_id)]")
    need_vehicle = fields.Boolean(compute='_compute_need_vehicle')
    vehicle_brand_domain = fields.Binary(string='Vehicle brand domain', compute='_compute_vehicle_brand_domain')
    vehicle_brand_id = fields.Many2one('helpdesk.vehicle.brand', 'Vehicle brand')
    vehicle_model = fields.Char(string='Vehicle model')
    vehicle_chasis = fields.Char(string='Vehicle chasis')
    need_year = fields.Boolean(compute='_compute_need_year')
    year_id = fields.Many2one('helpdesk.year', 'Year',
                              domain="['|',('tool_brand_ids','=', tool_brand_id),('product_ids','=', product_id)]")
    image = fields.Image(string='Image', help="Will attach a image to your ticket.")

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('helpdesk.ticket')
        return super(HelpdeskTicket, self).create(vals)

    @api.depends('partner_id')
    def _compute_tool_brand_domain(self):
        partner_tool = self.env['res.partner.tool']
        today = fields.Date.today()
        for ticket in self:
            if ticket.partner_id != False and ticket.partner_id.support_active:
                tool_brand_ids = partner_tool.search([
                    ('partner_id', '=', ticket.partner_id.id),
                    ('date_from', '<=', today),
                    ('date_to', '>=', today),
                    ('support_active', '=', True)
                ]).mapped('tool_brand_id').ids
                ticket.tool_brand_domain = tool_brand_ids
            else:
                ticket.tool_brand_domain = []

    @api.depends('tool_brand_id')
    def _compute_tool_model_domain(self):
        partner_tool = self.env['res.partner.tool']
        today = fields.Date.today()
        for ticket in self:
            if ticket.tool_brand_id != False:
                tool_models = partner_tool.search([
                    ('partner_id', '=', ticket.partner_id.id),
                    ('tool_brand_id', '=', ticket.tool_brand_id.id),
                    ('date_from', '<=', today),
                    ('date_to', '>=', today),
                    ('support_active', '=', True)
                ]).mapped('tool_model_id')
                ticket.tool_model_domain = tool_models.ids
            else:
                ticket.tool_model_domain = []

    @api.depends('ticket_type', 'tool_model_id', 'product_id')
    def _compute_vehicle_brand_domain(self):
        tool_service_vehicle = self.env['helpdesk.tool.service.vehicle']
        vehicle_brand = self.env['helpdesk.vehicle.brand']
        for ticket in self:
            if ticket.ticket_type == 'support':
                ticket.vehicle_brand_domain = tool_service_vehicle.search([('tool_model_id', '=', ticket.tool_model_id.id),
                                                                         ('product_id', '=', ticket.product_id.id)]).vehicle_brand_ids.ids
            else:
                ticket.vehicle_brand_domain = vehicle_brand.search([]).ids

    @api.depends('ticket_type', 'tool_model_id', 'product_id')
    def _compute_need_vehicle(self):
        for ticket in self:
            ticket.need_vehicle = ticket.ticket_type == 'assistance' or ticket.vehicle_brand_domain

    @api.depends('tool_brand_id','product_id')
    def _compute_need_year(self):
        for ticket in self:
            ticket.need_year = (ticket.tool_brand_id and ticket.tool_brand_id.year_ids) or \
                               (ticket.product_id and ticket.product_id.year_ids)

    @api.onchange('ticket_type', 'partner_id')
    def _onchange_ticket_type(self):
        self.tool_brand_id = False
        self.vehicle_chasis = False
        self._onchange_tool_brand()

    @api.onchange('tool_brand_id')
    def _onchange_tool_brand(self):
        self.tool_model_id = False
        self._onchange_tool_model()

    @api.onchange('tool_model_id')
    def _onchange_tool_model(self):
        self.product_id = False
        self.vehicle_brand_id = False
        self.vehicle_model = False
        self._onchange_product_id()

    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.year_id = False



