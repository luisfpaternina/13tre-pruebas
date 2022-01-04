# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging


from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.exceptions import UserError, AccessError


_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def _signup_create_user(self, values):
        current_website = self.env['website'].get_current_website()
        if request and current_website.specific_user_account:
            values['company_id'] = current_website.company_id.id
            values['company_ids'] = [(4, current_website.company_id.id)]
            values['website_id'] = current_website.id
        new_user = super(ResUsers, self)._signup_create_user(values)
        partner_record = self.env['res.partner'].with_context().sudo().search([('id', '=', new_user.partner_id.id)])
        

        vals = {
            'vat': values['vat'],
            'phone': values['phone'],
            'company_type': values['company_type'],
            'name': values['name'],
            'property_product_pricelist': 15
        }
        partner_record.write(vals)

        # Quitamos el acceso al portal
        usuario = self.env['res.users'].with_context().sudo().search([('id', '=', new_user.id)])

        if usuario:
            vals = {
                'lang': 'es_ES'
            }

            usuario.write(vals)
