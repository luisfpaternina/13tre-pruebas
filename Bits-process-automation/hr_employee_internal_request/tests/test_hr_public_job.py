from odoo.addons.hr_employee_internal_request.tests.common \
    import TestHrEmployeeInternalRequestBase
from odoo.addons.hr_employee_internal_request.controllers.main \
    import Website
from unittest.mock import patch, Mock
from odoo.addons.website.tools import MockRequest
from odoo.exceptions import ValidationError


class TestHrPublicJob(TestHrEmployeeInternalRequestBase):

    def setUp(self):
        super(TestHrPublicJob, self).setUp()
        self.url = ('odoo.addons.website.controllers.main.Website.publish')
        self.return_value = dict(
            status='accepted',
            transactionID='0000001')

    def test_action_public_job(self):
        controller = Website()

        with MockRequest(self.env):
            with patch(self.url, new=Mock(return_value=self.return_value)):
                controller.publish(self.job.id, self.job._name)

        with MockRequest(self.env):
            with patch(self.url, new=Mock(return_value=self.return_value)):
                controller.publish(self.job.id, self.job._name)

    def test_action_publish_res_user(self):
        controller = Website()

        with self.assertRaises(ValidationError):
            with MockRequest(self.env):
                with patch(self.url, new=Mock(return_value=self.return_value)):
                    controller.publish(
                        self.internal_request.id, self.internal_request._name)
