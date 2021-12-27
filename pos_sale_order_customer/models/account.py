# -*- coding: utf-8 -*-

import json

from odoo import _, api, fields, models


class Invoice(models.Model):
    _inherit = 'account.move'

    num_id_partner = fields.Char(
        compute="_compute_id_partner"
    )

    def _compute_id_partner(self):
        for record in self:
            if record.partner_id.is_company:
                record.num_id_partner = record.partner_id.vat
            else:
                record.num_id_partner = record.partner_id.number_identification
