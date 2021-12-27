# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class L10n(models.Model):

    _name = "bits_l10n_co"
    _description = "Lacation Workplace"

    divipola_code = fields.Char(
        string="Code")
    name = fields.Char(
        string="Name")
    place_type = fields.Selection([
        ('dp', 'Deparment'),
        ('mn', 'Municipality')
    ], string="Place Type")
