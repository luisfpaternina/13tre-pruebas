# coding: utf-8

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    brand = fields.Char(
        string='Brand',
        help='Reported brand in the Colombian electronic invoice.')
    customs_code = fields.Char(
        string='Customs Code',
        help="Mainly needed for Exportation Invoices")

    l10n_co_unit_measure_id = fields.Many2one(
        'l10n_co.unit_measures',
        string="Unit measures (DIAN)")

    l10n_co_foreign_client_applies = fields.Boolean(
        string="Apply for foreign client")

    l10n_co_brand = fields.Char(string="Brand")
    l10n_co_model = fields.Char(string="Model")
