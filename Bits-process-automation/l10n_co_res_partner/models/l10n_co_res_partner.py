# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class PartnerInfoExtended(models.Model):
    _inherit = 'res.partner'

    commercial_name = fields.Char('Commercial Name')

    # Tributate regime
    simplified_regimen = fields.Selection([
        ('6', "Simplified"),
        ('23', "Natural Person"),
        ('7', "Common"),
        ('11', "Great Taxpayer Autorretenedor"),
        ('22', "International"),
        ('25', "Common Autorretenedor"),
        ('24', "Great Contributor")],
        string="Tax Regime",
        default='6'
    )

    fiscal_regimen = fields.Selection([
        ('48', 'VAT sales tax'),
        ('49', 'Not responsible for VAT')],
        required=True, default='48'
    )

    # CIIU - Clasificación Internacional Industrial Uniforme
    ciiu = fields.Many2one('ciiu', "ISIC Activity")
    person_type = fields.Selection([
        ('1', "Juridical"),
        ('2', "Natural")],
        "Type of Person",
        default='1'
    )
