# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, tools


class UnitMeasures(models.Model):
    _name = "l10n_co.unit_measures"
    _description = "Unit measures"

    name = fields.Char(
        required=True,
        readonly=True)
    code = fields.Char(
        required=False,
        readonly=True)
