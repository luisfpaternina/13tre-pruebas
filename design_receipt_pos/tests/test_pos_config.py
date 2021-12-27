# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestPosConfig(TransactionCase):

    def setUp(self):
        super(TestPosConfig, self).setUp()
        self.new_config = self.env["pos.config"].create({
            "name": "usd config",
            "street": "Street Test"
        })

    def test_pos_config_street(self):

        self.assertEqual(self.street, "Street Test")
