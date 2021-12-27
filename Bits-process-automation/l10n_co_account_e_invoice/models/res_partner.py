# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResPartnerEInvoice(models.Model):
    _inherit = 'res.partner'

    fiscal_responsibility = fields.Many2one(
        'dian.fiscal.responsability'
    )
