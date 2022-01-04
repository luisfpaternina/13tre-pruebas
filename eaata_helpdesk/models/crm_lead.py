# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    tool_ids = fields.One2many('crm.lead.tool', 'lead_id', string="Tools")


    def _set_partner_tool(self, vals):
        if 'stage_id' in vals:
            PartnerTool = self.env['res.partner.tool']
            stage_id = self.env['crm.stage'].browse(vals['stage_id'])
            if stage_id.is_won:
                for lead in self:
                    if not lead.partner_id:
                        raise UserError(_('Please select a customer.'))
                    for crm_tool in lead.tool_ids:
                        tools = lead.partner_id.tool_ids.filtered(lambda tool: tool.name == crm_tool.name and
                                                                       tool.tool_brand_id == crm_tool.tool_brand_id and
                                                                       tool.tool_model_id == crm_tool.tool_model_id)
                        if not tools:
                            PartnerTool.create({
                                'name': crm_tool.name,
                                'tool_brand_id': crm_tool.tool_brand_id.id,
                                'tool_model_id': crm_tool.tool_model_id.id,
                                'partner_id': lead.partner_id.id,
                            })
                        else:
                            tools.write({'support_active': True})



    @api.model
    def create(self, vals):
        result = super(CrmLead, self).create(vals)
        result._set_partner_tool(vals)
        return result

    def write(self, vals):
        result = super(CrmLead, self).write(vals)
        self._set_partner_tool(vals)
        return result

    def action_set_lost(self, **additional_values):
        result = super(CrmLead, self).action_set_lost(**additional_values)
        PartnerTool = self.env['res.partner.tool']
        for lead in self:
            if not lead.partner_id:
                raise UserError(_('Please select a customer.'))
            for crm_tool in lead.tool_ids:
                tools = lead.partner_id.tool_ids.filtered(lambda tool: tool.name == crm_tool.name and
                                                                       tool.tool_brand_id == crm_tool.tool_brand_id and
                                                                       tool.tool_model_id == crm_tool.tool_model_id)
                if not tools:
                    PartnerTool.create({
                        'name': crm_tool.name,
                        'tool_brand_id': crm_tool.tool_brand_id.id,
                        'tool_model_id': crm_tool.tool_model_id.id,
                        'partner_id': lead.partner_id.id,
                        'support_active': False
                    })
                else:
                    tools.write({'support_active': False})
        return result


class CrmLeadTool(models.Model):
    _name = 'crm.lead.tool'

    name = fields.Char('Serial Number', required=True)
    tool_brand_id = fields.Many2one('helpdesk.tool.brand', 'Tool brand', required=True)
    tool_model_id = fields.Many2one('helpdesk.tool.model', 'Tool model', required=True,
                                   domain="[('tool_brand_id', '=', tool_brand_id)]")
    lead_id = fields.Many2one('crm.lead', 'Lead', required=True)
