# -*- coding: utf-8 -*-

from odoo.addons.l10n_co_account_e_invoice.tests.common \
    import TestFECommon
from odoo.exceptions import ValidationError


class TestDianFiscalResponsabilityLine(TestFECommon):

    def setUp(self):
        super(TestDianFiscalResponsabilityLine, self).setUp()

    def test_constraint_lines(self):
        responsability = self.DianFiscalResp.create({
            'code': 'test',
            'name': 'test'
        })
        resp_line1 = self.DianFiscalRespLine.create({
                'parent_id': responsability.id,
                'fiscal_responsability_id': self.responsability.id,
                'applicable_tax': [(6, 0, [self.tax_apply_2.id])]
            })
        with self.assertRaises(ValidationError):
            resp_line3 = self.DianFiscalRespLine.create({
                'parent_id': responsability.id,
                'fiscal_responsability_id': self.responsability_2.id,
                'applicable_tax': [(6, 0, [self.tax_apply_1.id])]
            })
