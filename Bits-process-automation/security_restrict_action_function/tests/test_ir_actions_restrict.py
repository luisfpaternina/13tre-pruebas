from datetime import datetime, date
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestIrActionsRestrict(TransactionCase):

    def setUp(self):
        super(TestIrActionsRestrict, self).setUp()
        self.groups_user = self.env['res.groups'].search([], limit=2)
        self.actions_restrict = self.env['ir.actions.restrict']
        self.restrict = self.actions_restrict.create({
            'name': "Test Restrict",
            'model': "example.model",
            'action_name': "get_test_actions",
            'action_code': "78954",
            'groups_access_ids': [(6, 0, self.groups_user.ids)],
            'message_show': "Permission Denied"
        })

        self.restrict_1 = self.actions_restrict.create({
            'name': "Test Restrict 1",
            'model': "example.model.1",
            'action_name': "get_test_actions",
            'action_code': "78954",
            'message_show': "Permission Denied"
        })

    def test_validate_user_groups(self):
        self.restrict.validate_user_groups()

    def test_validate_user_groups_error(self):
        self.env.user.write({
            'groups_id': False
        })
        with self.assertRaises(ValidationError):
            self.restrict.validate_user_groups()

    def test_validate_user_witout_groups(self):
        self.restrict_1.validate_user_groups()
