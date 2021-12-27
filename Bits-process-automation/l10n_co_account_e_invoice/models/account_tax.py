# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountTax(models.Model):
    _inherit = 'account.tax'

    tax_group_fe = fields.Selection([
        ('iva_fe', 'IVA FE'),
        ('ica_fe', 'ICA FE'),
        ('ico_fe', 'ICO FE'),
        ('other_fe', 'Other'),
        ('nap_fe', 'Not apply to DIAN FE')],
        string="Tax group DIAN FE",
        default='nap_fe')

    type_of_tax = fields.Many2one(
        'account.tax.type',
    )
    retention = fields.Boolean(default=False)

    @api.constrains('type_of_tax', 'type_tax_use')
    def _constraint_type_of_tax(self):
        if (self.company_id.active_tech_provider and
           (self.type_tax_use == 'sale' and not self.type_of_tax)):
            raise ValidationError(
                _('a sales tax cannot have the type_tax_use field empty')
            )
