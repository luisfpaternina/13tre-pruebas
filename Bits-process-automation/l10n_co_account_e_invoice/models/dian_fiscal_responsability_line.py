# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class DiaFiscalResponsabilityLine(models.Model):
    _name = 'dian.fiscal.responsability.line'
    _description = _(
        'DIAN tax matrix management'
    )

    parent_id = fields.Many2one(
        'dian.fiscal.responsability', required=True, ondelete='cascade'
    )
    fiscal_responsability_id = fields.Many2one(
        'dian.fiscal.responsability', required=True, ondelete='cascade'
    )
    applicable_tax = fields.Many2many(
        'account.tax.type',
        column1='dian_fiscal_responsability_line_id',
        column2='account_tax_type_id',
        domain="[('retention', '=', 'True')]"
    )

    @api.constrains('applicable_tax')
    def _check_validate_applicable_tax(self):
        for tax_retention in self.applicable_tax:
            if not tax_retention.retention:
                raise ValidationError(
                    _('The type of taxes to be applied must be '
                      ' withholding type')
                )

    _sql_constraints = [
        (
            'uk_dian_fiscal_responsability_line',
            'unique(parent_id, fiscal_responsability_id)',
            'You cannot have two taxes to apply to the same tax liability'
        )
    ]
