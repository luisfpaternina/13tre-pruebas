# -*- coding: utf-8 -*-
import logging
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase
from odoo.tests.common import Form

_logger = logging.getLogger('hr.payslip')


class TestHrPayrollApproval(TransactionCase):

    def setUp(self):
        super(TestHrPayrollApproval, self).setUp()
        self.send_email_payroll = self.env['send.email.payroll.approval']
        self.partner2 = self.env['res.partner'].create(
            {
                'company_type': 'person',
                'name': 'Ximena Vargas',
                'lang': 'en_US'
            }
        )
        self.partner = self.env['res.partner'].create(
            {
                'company_type': 'person',
                'name': 'Adrian Ayala Gonzalez',
                'email': 'adrian@gmail.com',
                'lang': 'en_US'
            }
        )
        self.job2 = self.env['hr.job'].create(
            {
                'name': 'Director de TI'
            }
        )
        self.job = self.env['hr.job'].create(
            {
                'name': 'Director administrativo y financiero'
            }
        )
        self.HrEmployee = self.env['hr.employee']
        self.employee2 = self.HrEmployee.create(
            {
                'name': 'Ximena Vargas',
                'job_id': self.job2.id,
                'address_home_id': self.partner2.id
            }
        )
        self.employee = self.HrEmployee.create(
            {
                'name': 'Adrian Ayala Gonzalez',
                'job_id': self.job.id,
                'address_home_id': self.partner.id,
                'work_email': 'adrian@gmail.com'
            }
        )
        self.default_work_entry = self.env['hr.work.entry.type'].create(
            {
                'name': 'My work entry',
                'code': 'MWE',
                'sequence': 25,
                'round_days': 'NO'
            }
        )
        self.salary_struct_type = self.env[
            'hr.payroll.structure.type'
        ].create(
            {
                'name': 'Type of test structure',
                'wage_type': 'monthly',
                'default_schedule_pay': 'monthly',
                'default_work_entry_type_id': self.default_work_entry.id
            }
        )
        self.calendar = self.env['resource.calendar'].create(
            {
                'name': 'Standard 40 hours/week',
                'hours_per_day': 8.00,
                'tz': 'America/Bogota',
                'full_time_required_hours': 40.00,
                'work_time_rate': 100.00
            }
        )
        self.contract = self.env['hr.contract'].create(
            {
                'name': 'Test contract',
                'structure_type_id': self.salary_struct_type.id,
                'resource_calendar_id': self.calendar.id,
                'wage': 100000,
                'date_start': datetime.strftime(
                    datetime.now() - timedelta(1), '%Y-%m-%d'
                )
            }
        )
        self.structure = self.env['hr.payroll.structure'].create(
            {
                'name': 'Test structure',
                'type_id': self.salary_struct_type.id,
            }
        )
        self.batch = self.env['hr.payslip.run'].create(
            {
                'name': 'Batch test',
                'date_start': datetime.strptime(
                    '2020/04/01', '%Y/%m/%d'
                ),
                'date_end': datetime.strptime(
                    '2020/04/30', '%Y/%m/%d'
                )
            }
        )
        self.payslip2 = self.env['hr.payslip'].create(
            {
                'employee_id': self.employee2.id,
                'name': 'Test payroll Ximena Vargas May 2020',
                'contract_id': self.contract.id,
                'struct_id': self.structure.id,
                'payslip_run_id': self.batch.id
            }
        )
        self.payslip = self.env['hr.payslip'].create(
            {
                'employee_id': self.employee.id,
                'name': 'Test payroll Adrian Ayala May 2020',
                'contract_id': self.contract.id,
                'struct_id': self.structure.id,
                'payslip_run_id': self.batch.id
            }
        )
        self.wizard_email_send = self.send_email_payroll.with_context(
            active_ids=[self.payslip.id, self.payslip2.id]
        ).create(
            {
                'is_email': False,
                'is_print': True,
                'printed': False,
                'template_id': self.env.ref(
                    'hr_payroll_approval.approval_email_template'
                ).id,
                'partner_ids': [(self.partner.id)],
                'payslip_ids': [(6, 0, [self.payslip.id, self.payslip2.id])]
            }
        )

    def setting_jobs_emails(self):
        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.emails_job_ids',
            [self.job.id])

    def send_for_approval(self):
        self.setting_jobs_emails()
        self.payslip.action_payslip_draft()
        self.payslip.compute_sheet()
        self.payslip.send_approval()

    def send_for_approval_without_settings_job(self):
        self.payslip.action_payslip_draft()
        self.payslip.compute_sheet()
        self.payslip.send_approval()

    def send_for_approval2(self):
        self.setting_jobs_emails()
        self.payslip2.compute_sheet()
        self.payslip2.send_approval()

    def test_verify_correct_draft(self):
        self.payslip.action_payslip_draft()
        self.assertEqual(self.payslip.state, 'draft')

    def test_verify_correct_compute_sheet(self):
        self.payslip.action_payslip_draft()
        self.payslip.compute_sheet()
        self.assertEqual(self.payslip.state, 'verify')

    def test_not_settings_jobs(self):
        with self.assertRaises(ValidationError):
            self.send_for_approval_without_settings_job()

    def test_verify_not_approve_payroll(self):
        self.send_for_approval()
        self.payslip.not_approve_payroll()
        self.assertEqual(self.payslip.general_state, 'rejected')

    def test_verify_approve_payroll(self):
        self.send_for_approval()
        self.payslip.approve_payroll()
        self.assertEqual(self.payslip.general_state, 'approved')

    def test_verify_incorrect_approve_payroll(self):
        self.payslip.action_payslip_draft()
        self.payslip.compute_sheet()
        with self.assertRaises(ValidationError):
            self.payslip.approve_payroll()

    def test_verify_correct_action_payslip_done(self):
        self.send_for_approval()
        self.payslip.approve_payroll()
        self.payslip.action_payslip_done()
        self.assertEqual(self.payslip.state, 'done')

    def test_verify_incorrect_action_payslip_done(self):
        self.send_for_approval()
        with self.assertRaises(ValidationError):
            self.payslip.action_payslip_done()

    def test_verify_correct_cancel_payslip(self):
        self.send_for_approval()
        self.payslip.action_payslip_cancel()
        self.assertEqual(self.payslip.general_state, 'disapproved')

    def test_verify_write(self):
        self.send_for_approval()
        self.payslip.write(
            {
                'name': 'Test payroll Adrian Ayala May 2021'
            }
        )

    def test_incorrect_way_to_send_for_approval(self):
        self.setting_jobs_emails()
        self.payslip.action_payslip_draft()
        with self.assertRaises(ValidationError):
            self.payslip.send_approval()

    def test_double_send_for_approval(self):
        self.send_for_approval()
        with self.assertRaises(ValidationError):
            self.payslip.send_approval()

    def test_rejected_and_sent_for_approval(self):
        self.send_for_approval()
        self.payslip.not_approve_payroll()
        self.payslip.send_approval()
        self.assertEqual(self.payslip.general_state, 'sent')

    def test_validation_change_information(self):
        self.payslip.action_payslip_draft()
        self.payslip.write(
            {
                'name': 'Test payroll Adrian Ayala May 2021'
            }
        )

    def test_verify_incorrect_modify_payslip(self):
        self.send_for_approval()
        self.payslip.approve_payroll()
        with self.assertRaises(ValidationError):
            self.payslip.write(
                {
                    'date': datetime.strftime(
                        datetime.now() - timedelta(1), '%Y-%m-%d'
                    )
                }
            )

    def test_verify_incorrect_not_approve(self):
        self.payslip.action_payslip_draft()
        with self.assertRaises(ValidationError):
            self.payslip.not_approve_payroll()

    def test_incorrect_action_payslip_cancel(self):
        self.send_for_approval()
        self.payslip.approve_payroll()
        with self.assertRaises(ValidationError):
            self.payslip.action_payslip_cancel()

    def test_incorrect_send_for_approval(self):
        self.send_for_approval()
        self.payslip.approve_payroll()
        with self.assertRaises(ValidationError):
            self.payslip.send_approval()

    def test_verify_correct_action_batch_done(self):
        self.send_for_approval()
        self.send_for_approval2()
        self.payslip2.approve_payroll()
        self.payslip.approve_payroll()
        self.batch.action_validate()

    def test_incorrect_action_batch_done(self):
        self.payslip.with_context(active_id=self.batch.id).compute_sheet()
        self.payslip2.with_context(active_id=self.batch.id).compute_sheet()
        self.send_for_approval()
        self.send_for_approval2()
        with self.assertRaises(ValidationError):
            self.batch.action_validate()

    def test_validate_batch_update_not_sent(self):
        self.payslip.action_payslip_draft()
        self.assertTrue(self.batch.internal_state == 'not sent')

    def test_validate_batch_update_sent(self):
        self.send_for_approval()
        self.send_for_approval2()
        self.assertTrue(self.batch.internal_state == 'sent')

    def test_validate_batch_update_rejected(self):
        self.send_for_approval()
        self.send_for_approval2()
        self.payslip.not_approve_payroll()
        self.payslip2.approve_payroll()
        self.assertTrue(self.batch.internal_state == 'rejected')

    def test_validate_batch_update_approved(self):
        self.send_for_approval()
        self.send_for_approval2()
        self.payslip.approve_payroll()
        self.payslip2.approve_payroll()
        self.assertTrue(self.batch.internal_state == 'approved')

    def test_validate_batch_update_disapproved(self):
        self.send_for_approval()
        self.send_for_approval2()
        self.payslip.action_payslip_cancel()
        self.payslip2.action_payslip_cancel()
        self.assertTrue(self.batch.internal_state == 'disapproved')

    def test_validation_not_update_batch(self):
        self.setting_jobs_emails()
        payroll3 = self.env['hr.payslip'].create(
            {
                'employee_id': self.employee.id,
                'name': 'Test payroll Adrian Ayala May 2020',
                'contract_id': self.contract.id,
                'struct_id': self.structure.id
            }
        )
        payroll3.compute_sheet()
        payroll3.send_approval()
        payroll3.approve_payroll()

    def test_validation_batch_none_state(self):
        self.payslip.compute_sheet()
        self.payslip.write(
            {
                'general_state': 'none'
            }
        )
        self.payslip.update_state_batch()

    def test_action_approval_window_with_lang(self):
        self.payslip.compute_sheet()
        self.payslip.action_payroll_approval_sent()

    def test_action_approval_window_not_lang(self):
        self.env.ref(
            'hr_payroll_approval.approval_email_template'
        ).lang = ''
        self.payslip.compute_sheet()
        self.payslip.action_payroll_approval_sent()

    def test_get_share_url_done(self):
        self.setting_jobs_emails()
        self.payslip.compute_sheet()
        self.payslip.send_approval()
        self.payslip.approve_payroll()
        self.payslip.action_payslip_done()
        self.payslip._get_share_url()

    def test_get_share_url_verify(self):
        self.payslip2.compute_sheet()
        self.payslip2._get_share_url()

    def test_set_to_draft(self):
        self.payslip.action_payslip_cancel()
        self.payslip2.action_payslip_cancel()
        self.batch.action_draft()

    def test_approve_batch(self):
        self.send_for_approval()
        self.send_for_approval2()
        self.batch.approve_batch()

    def test_disapprove_batch(self):
        self.send_for_approval()
        self.send_for_approval2()
        self.batch.disapprove_batch()

    def test_send_and_print_action(self):
        self.payslip.compute_sheet()
        self.payslip2.compute_sheet()
        self.wizard_email_send.send_and_print_action()

    def test_onchange_email(self):
        self.setting_jobs_emails()
        self.payslip.compute_sheet()
        self.payslip2.compute_sheet()
        self.wizard_email_send.onchange_is_email()
        self.wizard_email_send.update({
            'is_email': True
        })
        self.wizard_email_send.onchange_is_email()
        self.wizard_email_send.with_context(
            active_ids=[self.payslip.id, self.payslip2.id]
        ).send_and_print_action()

    def test_onchange_email_not_compose(self):
        self.setting_jobs_emails()
        self.payslip.compute_sheet()
        self.payslip2.compute_sheet()
        self.wizard_email_send.update({
            'is_email': True,
            'partner_ids': [(self.partner.id)]
        })
        self.wizard_email_send.update({
            'composer_id': False
        })
        self.wizard_email_send.onchange_is_email()
        self.composer_id = self.env['mail.compose.message'].create({
            'composition_mode': 'mass_mail',
            'template_id': self.env.ref(
                'hr_payroll_approval.approval_email_template'
            ).id,
        })
        self.wizard_email_send.update({
            'composer_id': self.composer_id.id
        })
        self.wizard_email_send.onchange_is_email()
        self.wizard_email_send.onchange_template_id()
        self.wizard_email_send._compute_composition_mode()

    def test_composition_mass_mail(self):
        self.payslip.compute_sheet()
        self.payslip2.compute_sheet()
        self.composer_id = self.env['mail.compose.message'].create({
            'composition_mode': 'mass_mail',
            'template_id': self.env.ref(
                'hr_payroll_approval.approval_email_template'
            ).id,
            'model': 'hr.payslip'
        })
        self.wizard_email_send.update({
            'composer_id': self.composer_id.id
        })
        self.wizard_email_send._compute_composition_mode()
        self.wizard_email_send.send_and_print_action()

    def test_not_is_print(self):
        self.payslip.compute_sheet()
        self.payslip2.compute_sheet()
        self.wizard_email_send.update({
            'is_print': False
        })
        self.wizard_email_send.send_and_print_action()

    def test_template_id_not_composer(self):
        self.payslip.compute_sheet()
        self.payslip2.compute_sheet()
        wizard_custom = self.send_email_payroll.with_context(
            active_ids=[self.payslip.id, self.payslip2.id]
        ).create({})
        wizard_custom.write(
            {
                'composer_id': False
            }
        )
        wizard_custom.onchange_template_id()

    def test_send_mail_mass(self):
        self.setting_jobs_emails()
        self.payslip.compute_sheet()
        self.payslip2.compute_sheet()
        send_email = self.send_email_payroll.with_context(
            active_ids=[self.payslip.id, self.payslip2.id]
        ).create(
            {
                'is_email': True,
                'is_print': True,
                'printed': False,
                'template_id': self.env.ref(
                    'hr_payroll_approval.approval_email_template'
                ).id,
                'partner_ids': [(self.partner.id)],
                'payslip_ids': [(6, 0, [self.payslip.id, self.payslip2.id])]
            }
        )
        composer_id = self.env['mail.compose.message'].create({
            'composition_mode': 'mass_mail',
            'template_id': self.env.ref(
                'hr_payroll_approval.approval_email_template'
            ).id,
            'model': 'hr.payslip',
        })
        send_email.update({
            'composer_id': composer_id.id
        })
        send_email.onchange_is_email()
        composer_id.with_context(
            active_ids=[self.payslip.id, self.payslip2.id],
            send_mass=True
        ).get_mail_values([self.payslip.id, self.payslip2.id])

    def test_get_restrict_action(self):
        self.payslip.get_restrict_action('other_method')
