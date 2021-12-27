# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class PaymentForms(models.Model):
    _name = "l10n_co.payment_forms"
    _description = "Forms payment"

    name = fields.Char(
        required=True,
        readonly=True)
    code = fields.Char(
        required=False,
        readonly=True)
