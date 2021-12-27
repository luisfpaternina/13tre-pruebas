# coding: utf-8

from odoo import fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    analytic_account_id = fields.Many2many(
        'account.analytic.account',
        string=_('Analytic Account'),
        help=_('Select analytic account related.'))
