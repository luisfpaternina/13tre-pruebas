# -*- coding: utf-8 -*-

from odoo.addons.l10n_co_res_partner.tests.common \
    import TestBaseResPartner


class TestCiiu(TestBaseResPartner):

    def setUp(self):
        super(TestCiiu, self).setUp()

    def test_compute_concat_name(self):
        self.ciiu._compute_concat_name()
        self.assertEqual(
            self.ciiu.name,
            'SECCIÓN A - AGRICULTURA, GANADERÍA, CAZA...'
        )

    def test_compute_set_type(self):
        self.assertEqual(
            self.ciiu.type,
            'view'
        )

        self.parent._compute_set_type()
        self.assertEqual(
            self.parent.type,
            'other'
        )
