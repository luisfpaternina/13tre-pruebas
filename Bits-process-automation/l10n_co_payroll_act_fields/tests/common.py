# -*- coding: utf-8 -*-

from odoo.fields import Date
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestBaseEinvoiceActFields(TransactionCase):

    def setUp(self):
        super(TestBaseEinvoiceActFields, self).setUp()
        self.ref_res_partner = self.env['res.partner']
        self.ref_act_fields = self.env['account.act.fields']
        self.act_field = self.ref_act_fields.create({
            'name': 'Field test',
            'code': '001',
            'mandatory': 'required',
            'condition_python': 'result = 1',
        })
