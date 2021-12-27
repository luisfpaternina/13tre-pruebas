from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestAuditlog(TransactionCase):

    def setUp(self):
        super(TestAuditlog, self).setUp()
        self.groups_model_id = self.env.ref("base.model_res_groups").id
        self.model_example = self.env.ref('base.model_res_groups')
        self.ResGroups = self.env['res.groups']

        self.groups_rule = self.env["auditlog.rule"].create(
            {
                "name": "testrule for groups",
                "model_id": self.groups_model_id,
                "log_read": True,
                "log_create": True,
                "log_write": True,
                "log_unlink": True,
                "state": "subscribed",
                "log_type": "full",
            }
        )

        self.group_test = self.ResGroups.create({
            'name': 'Group test'
        })
