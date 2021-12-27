# -*- coding: utf-8 -*-

from odoo.addons.l10n_co_e_invoice_act_fields.tests.common \
    import TestBaseEinvoiceActFields
from odoo.exceptions import UserError


class TestEinvoiceActFields(TestBaseEinvoiceActFields):

    def setUp(self):
        super(TestEinvoiceActFields, self).setUp()

    def test_compute_rule(self):
        localdict = dict()
        self.act_field._compute_rule(localdict)

        self.act_field.condition_python = ''
        res = self.act_field._compute_rule(localdict)
        self.assertFalse(res)
        self.act_field.condition_python = 'ERROR'
        with self.assertRaises(UserError):
            self.act_field._compute_rule(localdict)

    def test_satisfy_condition(self):
        localdict = dict()
        self.assertTrue(self.act_field._satisfy_condition(localdict))
        self.act_field.condition_select = 'python'
        self.act_field.validate_condition_select = 'result = True'
        self.act_field._satisfy_condition(localdict)
        self.act_field.validate_condition_select = 'ERROR'
        with self.assertRaises(UserError):
            self.act_field._satisfy_condition(localdict)

    def test_validate_required_field(self):
        localdict = dict()
        self.act_field.validate_required_field(localdict)
        self.act_field.condition_python = 'ERROR'
        with self.assertRaises(UserError):
            self.act_field.validate_required_field(localdict)

        self.act_field.mandatory = 'required'
        self.act_field.condition_python = 'result = ""'
        with self.assertRaises(UserError):
            self.act_field.validate_required_field(localdict)

        self.act_field.mandatory = 'condition'
        self.act_field.condition_python = 'ERROR'
        res = self.act_field.validate_required_field(localdict)
        self.assertTrue(res)
