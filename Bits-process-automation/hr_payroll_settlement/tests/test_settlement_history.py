# -*- coding: utf-8 -*-

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo.addons.hr_payroll_settlement.tests.common \
    import TestPayrollSettlement
from odoo.exceptions import ValidationError


class TestSettlementHistory(TestPayrollSettlement):

    def setUp(self):
        super(TestSettlementHistory, self).setUp()

    def test_onchange_employee(self):
        settlement1 = self.settlement_ref.new({
            'employee_id': False
        })
        settlement1._onchange_employee()

        settlement2 = self.settlement_ref.new({
            'employee_id': self.employee2.id,
            'contract_id': False,
        })
        settlement2._onchange_employee()

        contract = self.hr_contract.create({
            'name': "Contract Test",
            'date_start': datetime.now()-timedelta(days=365),
            'wage': 800000,
            'structure_type_id': self.structure_type.id,
            'employee_id': self.employee2.id,
            'state': 'open'
        })

        settlement2._onchange_employee()

        self.settlement._onchange_employee()

    def test_onchange_contract(self):
        self.settlement._onchange_contract()

    def test_onchange_date_end(self):
        self.settlement._onchange_date_end()
        settlement = self.settlement_ref.new({
            'date_end': False
        })
        settlement._onchange_date_end()

    def test_action_validate(self):
        self.batch_new.validate()
        self.batch_new.compute_payroll_news_board()
        self.batch_new2.validate()
        self.batch_new2.compute_payroll_news_board()
        stage_id = self.batch_ref._stage_find(
            domain=[('is_approved', '=', True)])
        line = self.env['hr.payroll.news'].search([
            ('batch_id', '=', self.batch_new.id),
        ], limit=5)
        line.write({
            'stage_id': stage_id
        })

        self.settlement.validate()

    def test_action_validate_without_payslip(self):
        self.settlement2.validate()

    def test_action_cancel(self):
        self.settlement.action_cancel()

    def test_action_draft(self):
        self.settlement.action_draft()

    def test_check_validate_date_end(self):
        settlement = self.settlement_ref.new({
            'employee_id': self.employee2.id,
            'contract_id': self.contract.id,
            'type_contract': 'fixed',
            'date_end': datetime.now()+timedelta(days=380),
        })
        with self.assertRaises(ValidationError):
            settlement._check_validate_date_end()

    def test_employee_whitout_contract(self):
        contract_employee3 = self.hr_contract.create({
            'name': "Contract Test",
            'date_start': datetime.now() - timedelta(days=365),
            'wage': 800000,
            'structure_type_id': self.structure_type.id,
            'employee_id': self.employee.id,
        })
        self.settlement3 = self.settlement_ref.new({
            'employee_id': self.employee.id,
            'date_payment': datetime.now(),
            'reason_for_termination': self.termination,
            'compensation': False,
        })
        self.settlement3._onchange_contract()

    def test_check_date_end(self):
        contract_employee4 = self.hr_contract.create({
            'name': "Contract Test",
            'date_start': datetime.now() - timedelta(days=365),
            'date_end': datetime.now(),
            'wage': 800000,
            'structure_type_id': self.structure_type.id,
            'employee_id': self.employee.id,
        })
        self.settlement4 = self.settlement_ref.new({
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'type_contract': 'fixed',
            'date_payment': datetime.now() - timedelta(days=100),
            'reason_for_termination': self.termination,
            'compensation': False,
        })
        self.settlement4._check_validate_date_end()
        self.settlement4._get_total_month(datetime.now(), datetime.now())
        # self.settlement4.update_date_contract()

    # def test_contract_non_fixed(self):
    #     self.settlement.write({
    #         'type_contract': 'non-fixed',
    #     })
    #     self.settlement.update_date_contract()
    #     date_start = datetime.now() - timedelta(days=120)
    #     end_date = datetime.now() - timedelta(days=20)
    #     self.settlement._get_total_month(date_start, end_date)

    def test_compute_work_days(self):
        self.settlement._compute_work_days()

    def test_get_total_pending_vacation_days(self):
        self.settlement._get_total_pending_vacation_days()

    def test_days_360(self):
        self.settlement.days_360(False, False)
        self.settlement.days_360(
            (
                datetime.now()-timedelta(days=365)
            ).date(), datetime.now().date()
        )

    def create_news_unpaid(self):
        structure_unpaid = self.env.ref(
            'bits_hr_payroll_news.structure_novelty_02'
        )
        news_unpaid = self.env['hr.payroll.news'].create({
            'name': 'AUSENTISMO NO REMUNERADO',
            'payroll_structure_id': structure_unpaid.id,
            'salary_rule_id': self.salary_rule_data.id,
            'salary_rule_code': self.salary_rule_data.code,
            'request_date_from': datetime.now() - timedelta(days=126),
            'request_date_to': datetime.now() - timedelta(days=110),
            'employee_payroll_news_ids': [
                (
                    0,
                    0,
                    {
                        'employee_id': self.employee.id,
                        'quantity': 16,
                        'amount': 35000,
                    }
                )
            ]
        })
        self.env['hr.employee.payroll.news'].create({
            'payroll_news_id': news_unpaid.id,
            'employee_id': self.employee.id,
            'quantity': 16,
            'amount': 35000,
        })

    def test_days_unpaid(self):
        self.create_news_unpaid()
        settlement4 = self.settlement_ref.new({
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'type_contract': 'fixed',
            'date_payment': datetime.now() - timedelta(days=100),
            'reason_for_termination': self.termination,
            'compensation': False,
        })
        settlement4.get_total_unpaid_news()

        config = self.env['res.config.settings'].create({})
        config.rule_unpaid_ids = [self.salary_rule_data.id]
        config.execute()
        settlement4.get_total_unpaid_news()
        settlement4.get_total_unpaid_news(
            datetime.now() - timedelta(days=100), datetime.now())

    def test_days_31(self):
        contract_test = self.hr_contract.new({
            'name': 'Contract test day 31',
            'date_start': date(2020, 1, 31),
            'date_end': datetime.now()+timedelta(days=365),
            'wage': 800000,
            'structure_type_id': self.structure_type.id
        })

        settlement_31 = self.settlement_ref.new({
            'employee_id': self.employee.id,
            'contract_id': contract_test.id,
            'type_contract': 'fixed',
            'date_payment': datetime.now() - timedelta(days=100),
            'date_end': date(2021, 1, 31),
            'reason_for_termination': self.termination,
            'compensation': False,
        })

        settlement_31.set_contract_duration()

    def test_action_validate_without_payslip2(self):

        settlement = self.settlement_ref.create({
            'employee_id': self.employee2.id,
            'contract_id': self.contract.id,
            'date_payment': datetime.now(),
            'reason_for_termination': self.termination,
            'compensation': False,
        })

        batch_new2 = self.batch_ref.create({
            'name': "Test Novelty",
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule.id,
            'employee_id': self.employee2.id,
            'method_number': 6,
            'original_value': 500000
        })
        batch_new2.validate()
        settlement.validate()
