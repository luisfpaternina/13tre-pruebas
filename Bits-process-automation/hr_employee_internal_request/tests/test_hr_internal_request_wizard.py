from odoo.addons.hr_employee_internal_request.tests.common \
    import TestHrEmployeeInternalRequestBase


class TestHrInternalRequestWizard(TestHrEmployeeInternalRequestBase):

    def setUp(self):
        super(TestHrInternalRequestWizard, self).setUp()

        self.internal_request_wizard = self.request_wizard.create({
            'reason_for_rejection': 'text example rejection',
            'reason_for_cancellation': 'text example cancellation'
        })

    def test_return_internal_request(self):
        self.internal_request_wizard.return_internal_request()

    def test_cancel_internal_request(self):
        self.internal_request_wizard.cancel_internal_request()

    def test_approved_internal_request(self):
        self.internal_request_wizard.approval_internal_request()
