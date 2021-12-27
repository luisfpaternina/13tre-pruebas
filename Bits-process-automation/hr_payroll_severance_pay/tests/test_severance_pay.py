from datetime import date
from odoo.addons.hr_payroll_severance_pay.tests.common \
    import TestCommonSeverancePay
from odoo.exceptions import UserError, ValidationError


class TestSeverancePay(TestCommonSeverancePay):

    def setUp(self):
        super(TestSeverancePay, self).setUp()

    def test_compute_sheet_september(self):
        self.september_payslip.compute_sheet()

    def test_compute_sheet_december(self):
        self.december_payslip.compute_sheet()

    def test_compute_sheet_jan(self):
        self.jan_payslip.compute_sheet()

    def test_compute_sheet_march(self):
        self.march_payslip.compute_sheet()

    def test_complete(self):
        self.september_payslip.sum_demo()

    def test_fixed_payslip(self):
        self.fixed_payslip.compute_sheet()

    # def test_onchange_line_list_invalid(self):
    #     record = self.wizard_ref.new({
    #         'date_from_f': '2020-05-06',
    #         'date_to_f': '2020-05-01',
    #     })
    #     res = record._onchange_line_list()
    #     self.assertTrue(res.get('warning', False))
