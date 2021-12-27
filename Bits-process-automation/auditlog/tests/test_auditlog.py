# Copyright 2015 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase
from unittest.mock import patch, Mock
from odoo.addons.website.tools import MockRequest
from odoo.http import request
from odoo.addons.auditlog.models.rule import DictDiffer


class AuditlogCommon(object):
    def test_LogCreation(self):
        """First test, caching some data."""

        self.groups_rule.subscribe()

        auditlog_log = self.env["auditlog.log"]
        group = self.env["res.groups"].create({"name": "testgroup1"})
        self.assertTrue(
            auditlog_log.search(
                [
                    ("model_id", "=", self.groups_model_id),
                    ("method", "=", "create"),
                    ("res_id", "=", group.id),
                ]
            ).ensure_one()
        )
        log = auditlog_log.search(
            [
                ("model_id", "=", self.groups_model_id),
                ("method", "=", "create"),
                ("res_id", "=", group.id),
            ]
        )
        log.write(
            {
                'http_request_id': self.env['auditlog.http.request'].create(
                    {
                        'name': '/web/dataset/call_kw/res.groups/create',
                        'root_url': 'http://10.40.60.132:8069/',
                    }
                )
            }
        )
        log.http_request_id._compute_display_name()
        log.http_request_id.name_get()
        log.http_request_id.current_http_request()
        group.write({"name": "Testgroup1"})
        self.assertTrue(
            auditlog_log.search(
                [
                    ("model_id", "=", self.groups_model_id),
                    ("method", "=", "write"),
                    ("res_id", "=", group.id),
                ]
            ).ensure_one()
        )
        group.unlink()
        self.assertTrue(
            auditlog_log.search(
                [
                    ("model_id", "=", self.groups_model_id),
                    ("method", "=", "unlink"),
                    ("res_id", "=", group.id),
                ]
            ).ensure_one()
        )

    def test_LogCreation2(self):
        """Second test, using cached data of the first one."""

        self.groups_rule.subscribe()

        auditlog_log = self.env["auditlog.log"]
        testgroup2 = self.env["res.groups"].create({"name": "testgroup2"})
        self.assertTrue(
            auditlog_log.search(
                [
                    ("model_id", "=", self.groups_model_id),
                    ("method", "=", "create"),
                    ("res_id", "=", testgroup2.id),
                ]
            ).ensure_one()
        )

    def test_LogCreation3(self):
        """Third test, two groups, the latter being the parent of the former.
        Then we remove it right after (with (2, X) tuple) to test the creation
        of a 'write' log with a deleted resource (so with no text
        representation).
        """

        self.groups_rule.subscribe()
        auditlog_log = self.env["auditlog.log"]
        testgroup3 = testgroup3 = self.env["res.groups"].create(
            {"name": "testgroup3"}
        )
        testgroup4 = self.env["res.groups"].create(
            {"name": "testgroup4", "implied_ids": [(4, testgroup3.id)]}
        )
        testgroup4.write({"implied_ids": [(2, testgroup3.id)]})
        self.assertTrue(
            auditlog_log.search(
                [
                    ("model_id", "=", self.groups_model_id),
                    ("method", "=", "create"),
                    ("res_id", "=", testgroup3.id),
                ]
            ).ensure_one()
        )
        self.assertTrue(
            auditlog_log.search(
                [
                    ("model_id", "=", self.groups_model_id),
                    ("method", "=", "create"),
                    ("res_id", "=", testgroup4.id),
                ]
            ).ensure_one()
        )
        self.assertTrue(
            auditlog_log.search(
                [
                    ("model_id", "=", self.groups_model_id),
                    ("method", "=", "write"),
                    ("res_id", "=", testgroup4.id),
                ]
            ).ensure_one()
        )

    def test_LogCreation4(self):
        """Fourth test, create several records at once (with create multi
        feature starting from Odoo 12) and check that the same number of logs
        has been generated.
        """

        self.groups_rule.subscribe()

        auditlog_log = self.env["auditlog.log"]
        groups_vals = [
            {"name": "testgroup1"},
            {"name": "testgroup3"},
            {"name": "testgroup2"},
        ]
        groups = self.env["res.groups"].create(groups_vals)
        # Ensure that the recordset returns is in the same order
        # than list of vals
        expected_names = ["testgroup1", "testgroup3", "testgroup2"]
        self.assertEqual(groups.mapped("name"), expected_names)

        logs = auditlog_log.search(
            [
                ("model_id", "=", self.groups_model_id),
                ("method", "=", "create"),
                ("res_id", "in", groups.ids),
            ]
        )
        self.assertEqual(len(logs), len(groups))

    def test_http_session_operations(self):
        self.groups_rule.subscribe()

        auditlog_log = self.env["auditlog.log"]
        group = self.env["res.groups"].create({"name": "testgroup1"})
        log = auditlog_log.search(
            [
                ("model_id", "=", self.groups_model_id),
                ("method", "=", "create"),
                ("res_id", "=", group.id),
            ]
        )
        session = self.env['auditlog.http.session'].create({
            'name': 'session test',
            'user_id': self.env.uid,
            'http_request_ids': log.http_request_id
        })
        session.name_get()
        session.current_http_session()

    def test_dict_diff(self):
        EMPTY_DICT = {}
        diff = DictDiffer(
            {}, {}
        )
        diff.removed()
        diff.unchanged()

    def test_patch_methods(self):
        # url = (
        #     'odoo.addons.auditlog.models.rule.AuditlogRule._patch_methods'
        # )
        # with MockRequest(self.env):
        #     with patch(url, new=Mock(return_value=False)):
        self.groups_model_id = self.env.ref("base.model_res_users").id
        rule_users = self.env["auditlog.rule"].create(
            {
                "name": "testrule1 for users",
                "model_id": self.groups_model_id,
                "log_read": False,
                "log_create": False,
                "log_write": True,
                "log_unlink": False,
                "log_type": "full",
            }
        )
        rule_users._patch_methods()


class TestAuditlogFull(TransactionCase, AuditlogCommon):
    def setUp(self):
        super(TestAuditlogFull, self).setUp()
        self.groups_model_id = self.env.ref("base.model_res_groups").id
        self.groups_rule = self.env["auditlog.rule"].create(
            {
                "name": "testrule for groups",
                "model_id": self.groups_model_id,
                "log_read": True,
                "log_create": True,
                "log_write": True,
                "log_unlink": True,
                "log_type": "full",
            }
        )

    def tearDown(self):
        self.groups_rule.unlink()
        super(TestAuditlogFull, self).tearDown()


class TestAuditlogFast(TransactionCase, AuditlogCommon):
    def setUp(self):
        super(TestAuditlogFast, self).setUp()
        self.groups_model_id = self.env.ref("base.model_res_groups").id
        self.groups_rule = self.env["auditlog.rule"].create(
            {
                "name": "testrule for groups",
                "model_id": self.groups_model_id,
                "log_read": True,
                "log_create": True,
                "log_write": True,
                "log_unlink": True,
                "log_type": "fast",
            }
        )

    def tearDown(self):
        self.groups_rule.unlink()
        super(TestAuditlogFast, self).tearDown()
