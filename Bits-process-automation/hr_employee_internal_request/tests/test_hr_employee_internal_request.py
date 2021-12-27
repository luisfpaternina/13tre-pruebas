from datetime import date
from odoo.addons.hr_employee_internal_request.tests.common \
    import TestHrEmployeeInternalRequestBase
from odoo.exceptions import UserError, ValidationError


class TestHrEmployeeInternalRequest(TestHrEmployeeInternalRequestBase):

    def setUp(self):
        super(TestHrEmployeeInternalRequest, self).setUp()

    def test_stages_flow(self):
        self.internal_request._get_stage_ids(False, [], False)

    def test_count_internal_request(self):
        self.job._compute_internal_request_count()
        self.job.action_get_internal_request_tree_view()
        
    def test_change_states(self):
        self.internal_request.action_request_sent()
        self.internal_request.action_request_approve()
        self.internal_request.action_request_process()
        self.internal_request.action_request_process_by_publish()
        self.internal_request.action_request_return()

    def test_open_wizard(self):
        self.internal_request.action_request_return()
        self.internal_request.action_request_cancel()

    def test_state_default(self):
        self.internal_request._get_stage_default()

    def test_re_sent_with_emails(self):
        self.stage.write({
            'email_profile_ids': [(6, 0, [self.job.id])]
        })

        request = self.request.create({
            "name": "Internal Request",
            "job_position": self.job.id,
            "stage_id": self.stage.id
        })

    def test_cancel_internal_request(self):
        user_admin = self.env.ref('base.user_admin')

        self.stage_cancel.write({
            'email_profile_ids': [(6, 0, [self.job.id])],
            'template_id': self.template.id
        })
        self.internal_request.write({
            'stage_id': self.stage_cancel.id,
            'create_uid': user_admin.id
        })

    def test_return_internal_request(self):
        user_admin = self.env.ref('base.user_admin')

        self.stage_cancel.write({
            'email_profile_ids': [(6, 0, [self.job.id])],
            'template_id': self.template.id
        })
        self.internal_request.write({
            'stage_id': self.stage_cancel.id,
            'create_uid': user_admin.id
        })

    def test_action_request_process_by_publish(self):
        stage_approved = self.env.ref(
            'hr_employee_internal_request.internal_request_stage_3')
        self.internal_request.write({
            'stage_id': stage_approved.id
        })

        self.internal_request.action_request_process_by_publish()

    def test_not_find_validate_privileges(self):
        self.internal_request._validate_privileges('not_exist')
    
    def test_onchange_internal_request_name(self):
        self.internal_request._onchange_internal_request_name()
    
    def test_compute_job_position(self):
        self.internal_request._compute_job_position()
    
    def test_compute_job_position_project(self):
        self.internal_request._compute_job_position_project()
    
    def test_create(self):
        self.internal_request.create()
        
    def test_validate_number_of_employees(self):
        self.internal_request._validate_number_of_employees()

    def test_create_data(self):
        # Create a new record with the test
        test_code = self.env['hr.employee.internal.request'].create({
            'code': '000001'
        })
        test_code1 = self.env['hr.employee.internal.request'].create({
            'code': 'New'
        })
        test_code2 = self.env['hr.employee.internal.request'].create({
            'code': '000002'
        })
        
    def test_get_users_emails(self):
        self.internal_request.get_users_emails()

    def test_compute_internal_request_count(self):
        self.job._compute_internal_request_count()

    def test_action_get_internal_request_tree_view(self):
        self.job.action_get_internal_request_tree_view()

