from unittest.mock import patch, Mock
from odoo.addons.website.tools import MockRequest
from .common import (TestAuditlog)


class TestHttp(TestAuditlog):

    def setUp(self):
        super(TestHttp, self).setUp()

    def test_create_group(self):
        self.groups_rule.subscribe()
        self.groups_rule._register_hook()

        self.ResGroups.create({
            'name': 'Group test'
        })

    def test_write_group(self):
        self.groups_rule.subscribe()
        self.groups_rule._register_hook()

        group = self.env.ref('base.group_erp_manager')
        group.with_context(self.env.context).write({
            'name': 'Access Rights Update Test'
        })

    def test_delete_group(self):
        self.groups_rule.subscribe()
        self.groups_rule._register_hook()

        self.group_test.unlink()

    def test_with_context(self):
        self.groups_rule.subscribe()
        self.groups_rule._register_hook()

        result = self.groups_rule.read([])
