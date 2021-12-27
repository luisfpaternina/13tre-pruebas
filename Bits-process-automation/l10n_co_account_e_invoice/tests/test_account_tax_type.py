# -*- coding: utf-8 -*-

from odoo.addons.l10n_co_account_e_invoice.tests.common \
    import TestFECommon


class TestAccountTaxType(TestFECommon):

    def setUp(self):
        super(TestAccountTaxType, self).setUp()

    def test_method_show_tax(self):
        self.tax_type.get_tax()
