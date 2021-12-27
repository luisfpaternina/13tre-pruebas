from datetime import date
from odoo.addons.bits_hr_payroll_news_batch.tests.common \
    import TestBitsHrPayrollNewsBatchBase
from odoo.exceptions import UserError, ValidationError


class TestBitsHrPayrollNewsBatch(TestBitsHrPayrollNewsBatchBase):

    def setUp(self):
        super(TestBitsHrPayrollNewsBatch, self).setUp()

    def test_employee_not_found(self):
        with self.assertRaises(ValidationError):
            self.batch_ref.create({
                'name': 'Payroll batch',
                'payroll_structure_id': self.payroll_structure.id,
                'salary_rule_code': 'TSTR',
                'identification_id': '75314666',
                'method_number': 1,
                'fixed_value': 26000
            })

    def test_salary_rule_not_found(self):
        with self.assertRaises(ValidationError):
            self.batch_ref.create({
                'name': 'Payroll batch',
                'payroll_structure_id': self.payroll_structure.id,
                'salary_rule_code': 'TSTR-1',
                'identification_id': '75395146',
                'method_number': 1,
                'fixed_value': 26000
            })

    def test_compute_payroll_news_board(self):
        self.batch_new.compute_payroll_news_board()
        self.assertEqual(
            len(self.batch_new.children_ids),
            self.batch_new.method_number
        )

    def test_compute_book_value(self):
        self.batch_new.compute_payroll_news_board()
        stage_id = self.batch_ref._stage_find(domain=[('is_won', '=', True)])
        line = self.env['hr.payroll.news'].search([
            ('batch_id', '=', self.batch_new.id),
        ], limit=5)
        line.write({
            'stage_id': stage_id
        })
        self.batch_new._compute_book_value()

    def test_validate(self):
        self.batch_new.compute_payroll_news_board()
        self.batch_new._onchange_name()
        self.batch_new.validate()
        self.batch_new.compute_payroll_news_board()

    def test_action_set_to_close(self):
        self.batch_new.compute_payroll_news_board()
        stage_id = self.batch_ref._stage_find(domain=[('is_won', '=', True)])

        line = self.env['hr.payroll.news'].search([
            ('batch_id', '=', self.batch_new.id),
        ], limit=1)
        line.write({
            'stage_id': stage_id
        })
        self.batch_new.action_set_to_close()

    def test_set_to_draft(self):
        self.batch_new.compute_payroll_news_board()
        with self.assertRaises(ValidationError):
            self.batch_new.set_to_draft()

    def test_set_to_draft_fixed(self):
        stage_id = self.batch_fixed._stage_find(domain=[('sequence', '=', 1)])

        self.batch_fixed.compute_payroll_news_board()
        self.batch_fixed.children_ids.write({
            'stage_id': stage_id
        })

        self.batch_fixed.set_to_draft()

    def test_compute_payroll_news_board_fixed(self):
        self.batch_fixed.compute_payroll_news_board()
        self.batch_fixed._compute_date_end()

    def test_compute_date_end(self):
        self.batch_current._compute_date_end()

    def test_compute_all_payrolls(self):
        self.batch_fixed.write({
            'state': 'open'
        })

        self.batch_fixed._compute_all_payroll_news_board()
        self.batch_fixed._approved_all_batch()
        self.batch_new._compute_all_payroll_news_board()
        self.batch_new._approved_all_batch()

    def test_generate_fixed_novelties(self):
        self.batch_fixed.write({
            'state': 'open'
        })

        self.batch_last_month.compute_payroll_news_board()
        self.batch_fixed._generate_fixed_novelties()

    def test_generate_fixed_novelties_2(self):
        self.batch_fixed.write({
            'state': 'open'
        })

        self.batch_fixed._generate_fixed_novelties()

    def test_change_check_make_depreciation(self):
        self.batch_fixed._change_depreciation()
        self.batch_fixed.write({
            'make_depreciation': True
        })
        self.batch_fixed._change_depreciation()
