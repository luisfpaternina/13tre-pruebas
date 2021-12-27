from datetime import date
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo.addons.hr_payroll_paycheck.tests.common \
    import TestPayrollPaycheck
from odoo.exceptions import UserError, ValidationError


class TestHrPayrollPaycheck(TestPayrollPaycheck):

    def setUp(self):
        super(TestHrPayrollPaycheck, self).setUp()

    def test_action_paycheck_sent(self):
        res = self.payslip.action_paycheck_sent()
        self.payslip._compute_month_payroll()
        self.payslip._compute_year_payroll()
        self.payslip._compute_text_copyright()
        res = self.payslip.action_payslip_print()
        res = self.payslip._get_share_url()

    def test_wizard_send_email(self):
        res = self.payslip.action_paycheck_sent()
        context = res.get('context')
        context['active_ids'] = self.payslip.ids
        del context['mark_payslip_as_sent']

        wizard = self.wizard_ref.with_context(
            active_ids=self.payslip.ids).create({'is_email': False})
        wizard._send_email()
        wizard.write({
            'is_email': False,
            'is_print': False
        })
        wizard._send_email()

    def test_wizard_compute_onchange(self):
        wizard = self.wizard_ref.with_context(
            active_ids=self.payslip.ids).new({'composer_id': False})
        wizard.onchange_is_email()
        wizard.onchange_template_id()

        wizard = self.wizard_ref.with_context(
            active_ids=self.payslip.ids).new({
                'is_email': False, 'composer_id': False})
        wizard.onchange_template_id()
        wizard.onchange_is_email()

        res = self.payslip.action_paycheck_sent()
        context = res.get('context')
        context['active_ids'] = self.payslip.ids

        wizard = self.wizard_ref.with_context(context).create({})
        wizard.default_get({})
        wizard._compute_composition_mode()
        wizard.onchange_template_id()
        wizard.onchange_is_email()

    def test_wizard_send_and_print_action(self):
        res = self.payslip.action_paycheck_sent()
        context = res.get('context')
        context['active_ids'] = self.payslip.ids
        wizard = self.wizard_ref.with_context(context).create({})
        wizard.send_and_print_action()

        wizard.write({
            'is_email': False,
            'is_print': False
        })
        wizard.send_and_print_action()

    def test_wizard_send_and_print_action_mass(self):
        res = self.payslip.action_paycheck_sent()
        context = res.get('context')
        context['active_ids'] = [self.payslip.id, self.payslip2.id]
        context['mark_payslip_as_sent'] = False

        wizard = self.wizard_ref.with_context(context).create({})
        wizard._compute_composition_mode()
        wizard.send_and_print_action()
        self.payslip._round_value_payslip(32999.90)
