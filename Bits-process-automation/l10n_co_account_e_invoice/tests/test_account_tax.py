# -*- coding: utf-8 -*-

from odoo.addons.l10n_co_account_e_invoice.tests.common \
    import TestFECommon
from odoo.exceptions import ValidationError


class TestAccountTax(TestFECommon):

    def setUp(self):
        super(TestAccountTax, self).setUp()

    def test_create_without_type(self):
        self.env['account.tax'].search([('name', '=', 'Tax Test')]).unlink()
        config = self.env['res.config.settings'].create({})
        config.active_tech_provider = True
        config.provider_id = self.tech_provider_1.id
        config.execute()
        info = {
            'name': 'Tax Test',
            'amount': 23,
            'type_tax_use': 'sale',
        }
        with self.assertRaises(ValidationError):
            self.env['account.tax'].create(info)

        info['type_of_tax'] = self.tax_type.id
        info['name'] = 'Tax Test 2'
        tax = self.env['account.tax'].create(info)
        self.tax_type.get_count_tax()

    def test_configure_l10n_co_account_tax_data(self):
        self.env['res.config.settings'].l10n_co_install_group_taxes()
        chart_template = self.env.ref(
            'l10n_co.l10n_co_chart_template_generic',
            raise_if_not_found=False
        )
        self.env['account.tax.template']._configure_l10n_co_account_tax_data(
            self.company,
            'l10n_ae.uae_chart_template_standard'
        )
        self.company.write({
            'chart_template_id': chart_template.id
        })
        self.env['account.tax.template']._configure_l10n_co_account_tax_data(
            self.company,
        )
