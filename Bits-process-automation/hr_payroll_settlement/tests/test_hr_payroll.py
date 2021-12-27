from datetime import date
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo.addons.hr_payroll_settlement.tests.common \
    import TestPayrollSettlement
from odoo.exceptions import UserError, ValidationError


class TestHrPayroll(TestPayrollSettlement):

    def setUp(self):
        super(TestHrPayroll, self).setUp()

    def test_get_base_local_dict(self):
        self.payslip._get_base_local_dict()

    def test_get_contract_type(self):
        res = self.payslip._get_base_local_dict()
        indemnities = res.get('indemnities')
        _type = indemnities.get_contract_type('fixed')
        self.assertFalse(_type)

    def test_calculation_indenminazion_fixed(self):
        res = self.payslip._get_base_local_dict()
        indemnities = res.get('indemnities')
        result = indemnities.calculation_indenminazion_fixed()

    def test_calculation_indenminazion_non_fixed(self):
        res = self.payslip._get_base_local_dict()
        indemnities = res.get('indemnities')
        result = indemnities.calculation_indenminazion_non_fixed()

    def test_compute_settlement_holidays_pay(self):
        res = self.payslip._get_base_local_dict()
        indemnities = res.get('indemnities')

        result = indemnities.compute_settlement_holidays_pay(
            'WORK100',
            codes=[],
            from_date=self.payslip.date_from,
            to_date=self.payslip.date_to)

        self.settlement.write({
            'work_days': 720,
            'payslip_id': self.payslip.id
        })

        result = indemnities.compute_settlement_holidays_pay(
            'WORK100',
            codes=['60', '65', '70', '75', '321'],
            from_date=self.payslip.date_from,
            to_date=self.payslip.date_to)

        result = indemnities.compute_settlement_holidays_pay(
            'WORK100',
            codes=[],
            from_date=self.payslip.date_from,
            to_date=self.payslip.date_to)

    def test_compute_settlement_legal_premium(self):
        self.settlement.write({
            'work_days': 720,
            'payslip_id': self.payslip.id
        })
        res = self.payslip._get_base_local_dict()
        indemnities = res.get('indemnities')

        self.settlement.write({
            'payslip_id': self.payslip.id,
            'date_end': datetime.now().replace(day=1, month=7).date()
        })

        self.batch_new.write({
            'first_depreciation_date': datetime.now().replace(
                day=1, month=1).date()
        })
        self.batch_new.compute_payroll_news_board()
        self.batch_new.validate()

        self.batch_new.children_ids.write({
            'stage_id': self.stage_approved.id,
        })

        result = indemnities.compute_settlement_legal_premium(
            '120',
            codes=['60', '65', '70', '75', '321'],
            period=2)

        result = indemnities.compute_settlement_legal_premium(
            '120',
            codes=[],
            period=2)

    def test_compute_settlement_severance_pay(self):
        res = self.payslip._get_base_local_dict()
        indemnities = res.get('indemnities')

        self.batch_new.write({
            'first_depreciation_date': datetime.now().replace(
                day=1, month=1).date()
        })
        self.batch_new.compute_payroll_news_board()
        self.batch_new.validate()

        self.batch_new.children_ids.write({
            'stage_id': self.stage_approved.id,
        })

        result = indemnities.compute_settlement_severance_pay(
            'WORK100',
            codes=['60', '65', '70', '75', '321'])

        result = indemnities.compute_settlement_severance_pay(
            'WORK100',
            period=24,
            codes=[])

        result = indemnities.compute_settlement_severance_pay(
            'WORK100',
            period=1,
            codes=[])

    def test_compute_settlement_severance_pay_interest(self):
        res = self.payslip._get_base_local_dict()
        indemnities = res.get('indemnities')
        result = indemnities.compute_settlement_severance_pay_interest(
            'WORK100',
            codes=['60', '65', '70', '75', '321'],
            from_date=self.payslip.date_from,
            to_date=self.payslip.date_to)

    def test_get_settlement(self):
        res = self.payslip._get_settlement()
        self.assertFalse(res)
