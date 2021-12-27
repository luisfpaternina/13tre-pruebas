# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.tests import common, Form


class TestAccount(TransactionCase):

    def setUp(self):
        super(TestAccount, self).setUp()
        self.product_tmpl_id = self.env['product.template']
        self.partner_id = self.env['res.partner']
        self.pos_session_id = self.env['pos.session']
