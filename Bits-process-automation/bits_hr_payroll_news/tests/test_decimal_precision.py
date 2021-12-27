from odoo.exceptions import ValidationError
from .test_bits_hr_payroll_news import (TestBitsHrPayrollNews)


class TestDecimalPrecision(TestBitsHrPayrollNews):

    def setUp(self):
        super(TestDecimalPrecision, self).setUp()

    def test_get_rounding(self):
        total = self.env['decimal.precision'].get_rounding(
            'PAYROLLTEST', 32112)
        self.assertEqual(32200.0, total)
