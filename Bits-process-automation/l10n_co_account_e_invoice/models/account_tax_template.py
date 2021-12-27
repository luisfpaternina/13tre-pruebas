# coding: utf-8

import logging
from odoo import fields, models
_logger = logging.getLogger(__name__)


class AccountTaxTemplate(models.Model):
    _inherit = 'account.tax.template'

    type_of_tax = fields.Many2one(
        'account.tax.type'
    )

    def _configure_l10n_co_account_tax_data(self, company, _ref=None):

        if not _ref:
            _ref = 'l10n_co.l10n_co_chart_template_generic'
        _logger.debug('_configure_l10n_co_account_tax_data')
        chart_template = self.env.ref(
            _ref,
            raise_if_not_found=False
        )

        if chart_template:
            tax_templates = self.env['account.tax.template'].search(
                [
                    ('chart_template_id', '=', chart_template.id),
                    ('type_tax_use', '=', 'sale'),
                    ('type_of_tax', '!=', False)
                ]
            )
            xml_ids = tax_templates.get_external_id()
            for tax_template in tax_templates:
                module, xml_id = xml_ids.get(tax_template.id).split('.')
                tax = self.env.ref(
                    '%s.%s_%s' % (module, company.id, xml_id),
                    raise_if_not_found=False
                )
                if tax:
                    tax.type_of_tax = tax_template.type_of_tax
