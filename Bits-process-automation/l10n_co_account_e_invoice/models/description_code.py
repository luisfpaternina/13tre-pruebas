# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, tools


class DescriptionCode(models.Model):
    _name = "l10n_co.description_code"
    _description = "Descriptions code for credit notes"

    name = fields.Char(
        required=True,
        readonly=True)
    code = fields.Char(
        required=False,
        readonly=True)
    type = fields.Selection([
        ('credit', 'Credit'),
        ('debit', 'Debit')],
        string="Document type",
        required=False,
        readonly=True)
