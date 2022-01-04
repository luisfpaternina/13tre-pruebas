# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = ['account.move']
    #
    # horas_reales = fields.Float(
    #     string='Horas Reales',
    #     required=False)
