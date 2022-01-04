# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    tool_ids = fields.One2many('sale.subscription.tool', 'subscription_id', string="Tools")
    partner_id2 = fields.Many2one('res.partner', string='Cliente Assinatura')
    notes = fields.Char('Notes')

    def _set_partner_tool(self, vals):
        PartnerTool = self.env['res.partner.tool']
        for item in self:

            if 'stage_id' in vals:
                stage_id = self.env['sale.subscription.stage'].browse(vals['stage_id'])
            else:
                stage_id = item.stage_id

            if not stage_id.fold and not stage_id.in_progress:
                continue

            for sub_tool in item.tool_ids:
                tools = item.partner_id2.tool_ids.filtered(lambda tool: tool.name == sub_tool.name and tool.tool_brand_id == sub_tool.tool_brand_id and tool.tool_model_id == sub_tool.tool_model_id)

                if stage_id.in_progress:                
                    if not tools:
                        PartnerTool.create({
                            'name': sub_tool.name,
                            'tool_brand_id': sub_tool.tool_brand_id.id,
                            'tool_model_id': sub_tool.tool_model_id.id,
                            'partner_id': item.partner_id2.id,
                            'date_from': sub_tool.date_from,
                            'date_to': sub_tool.date_to,
                            'support_active': sub_tool.support_active,
                            'fecha_actualizacion': sub_tool.fecha_actualizacion,
                        })
                    else:
                        tools.write({
                            'date_from': sub_tool.date_from,
                            'date_to': sub_tool.date_to,
                            'support_active': sub_tool.support_active,
                            'fecha_actualizacion': sub_tool.fecha_actualizacion,
                        })

                elif stage_id.fold:
                    if tools:
                        tools.write({
                            'date_from': sub_tool.date_from,
                            'date_to': sub_tool.date_to,
                            'support_active': sub_tool.support_active,
                            'fecha_actualizacion': sub_tool.fecha_actualizacion,
                        })

    @api.model
    def create(self, vals):
        result = super(SaleSubscription, self).create(vals)
        result._set_partner_tool(vals)
        return result

    def write(self, vals):
        result = super(SaleSubscription, self).write(vals)
        self._set_partner_tool(vals)
        return result

class SaleSubscriptionTool(models.Model):
    _name = 'sale.subscription.tool'

    name = fields.Char('Serial Number', required=True)
    tool_brand_id = fields.Many2one('helpdesk.tool.brand', 'Tool brand', required=True)
    tool_model_id = fields.Many2one('helpdesk.tool.model', 'Tool model', required=True, domain="[('tool_brand_id', '=', tool_brand_id)]")
    date_from = fields.Date(string='From', required=True)
    date_to = fields.Date(string='To')
    support_active = fields.Boolean(string='Support active')
    fecha_actualizacion = fields.Date(string='Fecha de Actualización')
    subscription_id = fields.Many2one('sale.subscription', 'Subscription', required=True)
