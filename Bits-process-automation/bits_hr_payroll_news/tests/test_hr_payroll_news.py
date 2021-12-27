from odoo.exceptions import ValidationError
from datetime import datetime, date
from .test_bits_hr_payroll_news import (TestBitsHrPayrollNews)


class TestHrPayrollNews(TestBitsHrPayrollNews):

    def setUp(self):
        super(TestHrPayrollNews, self).setUp()

    def test_default_stage_id(self):
        result = self.payroll_new._default_stage_id()

    def test_onchange_payroll_structure_id(self):
        self.payroll_new._onchange_payroll_structure_id()

    def test_onchange_salary_rule_id(self):
        payroll_new = self.hr_payroll_new.new({
            'name': "Test Novelty",
            'payroll_structure_id': self.payroll_structure.id
        })
        result = payroll_new._onchange_salary_rule_id()
        self.assertEqual(result, {})

        self.payroll_new._onchange_salary_rule_id()

    def test_compute_date_deadline_formatted(self):
        self.payroll_new._compute_date_deadline_formatted()

    def test_compute_kanban_state_label(self):
        self.payroll_new._compute_kanban_state_label()
        self.assertEqual(self.payroll_new.kanban_state_label,
                         self.payrol_news_stage.legend_normal)
        payroll_new = self.hr_payroll_new.create({
            'name': "Test Novelty",
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule.id,
            'kanban_state': "done",
            'stage_id': self.payrol_news_stage.id,
            'employee_payroll_news_ids': [(0, 0, {
                'employee_id': self.employee.id,
                'quantity': 2,
                'amount': 100
            })]
        })
        payroll_new._compute_kanban_state_label()
        self.assertEqual(payroll_new.kanban_state_label,
                         self.payrol_news_stage.legend_done)

        payroll_new_1 = self.hr_payroll_new.create({
            'name': "Test Novelty",
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule.id,
            'kanban_state': "blocked",
            'stage_id': self.payrol_news_stage.id,
            'employee_payroll_news_ids': [(0, 0, {
                'employee_id': self.employee.id,
                'quantity': 2,
                'amount': 100
            })]
        })
        payroll_new_1._compute_kanban_state_label()
        self.assertEqual(payroll_new_1.kanban_state_label,
                         self.payrol_news_stage.legend_blocked)

    def test_read_group_stage_ids(self):
        self.payroll_new._read_group_stage_ids(False, [], False)

    def test_stage_find(self):
        self.payroll_new._stage_find([])

    def test_compute_employee_count(self):
        self.payroll_new._compute_employee_count()
        self.assertEqual(self.payroll_new.employee_count, 2)
        self.hr_payroll_new._compute_employee_count()

    def test_hr_payroll_news_write(self):
        payrol_news_stage = self.hr_payroll_news_stage.create({
            'name': "Stage Test"
        })
        self.payroll_new.write({
            'stage_id': payrol_news_stage.id
        })
        self.assertEqual(self.payroll_new.kanban_state, 'normal')
        self.payroll_new.write({
            'stage_id': payrol_news_stage.id,
            'kanban_state': "done"
        })
        self.assertEqual(self.payroll_new.kanban_state, 'done')

    def test_onchange_stage_id(self):
        payroll_new = self.hr_payroll_new.new({
            'name': "Test Novelty",
            'payroll_structure_id': self.payroll_structure.id
        })
        payroll_new._onchange_stage_id()

    def test_hr_payroll_news_import_raise(self):

        test = {
            'name': 'Novedad He Diurnas',
            'salary_rule_code': 'NOTEXIST',
            'payroll_structure_id': False,
            'user_id': 6,
            'employee_payroll_news_ids': [(0, 0, {
                'employee_id': self.employee.id,
                    'payroll_news_id': False,
                    'quantity': 2,
                    'amount': 100
                })
            ]
        }

        with self.assertRaises(ValidationError):
            self.hr_payroll_new.create(test)

        test['salary_rule_code'] = '145'
        del(test['employee_payroll_news_ids'])

        with self.assertRaises(ValidationError):
            self.hr_payroll_new.create(test)

        test['employee_payroll_news_ids'] = [(
            0,
            False,
            {
                'identification_id': '123456789',
                'quantity': 10.0,
                'amount': 25000.0
            }
        )]

        with self.assertRaises(ValidationError):
            self.hr_payroll_new.create(test)

        test['employee_payroll_news_ids'][0][2]['amount'] = False

        with self.assertRaises(ValidationError):
            self.hr_payroll_new.create(test)

        test['employee_payroll_news_ids'][0][2]['identification_id'] = self.\
            employee.identification_id,

        with self.assertRaises(ValidationError):
            self.hr_payroll_new.create(test)

    def test_hr_payroll_news_import(self):
        self.contract.write({'state': 'open'})
        test = {
            'name': 'Novedad TEST 2',
            'salary_rule_code': 145,
            'payroll_structure_id': False,
            'employee_payroll_news_ids': [(
                0,
                False,
                {
                    'identification_id': self.employee.identification_id,
                    'quantity': 10.0,
                    'amount': False
                }
            )]
        }

        self.hr_payroll_new.create(test)

    def test_hr_payroll_news_not_satisfy_condition(self):
        self.salary_rule_0.write({
            'condition_select': "python",
            'condition_python': "10>1"
        })

        test = {
            'name': 'Novedad TEST 2',
            'salary_rule_code': self.salary_rule_0.code,
            'payroll_structure_id': False,
            'employee_payroll_news_ids': [(
                0,
                False,
                {
                    'identification_id': self.employee.identification_id,
                    'quantity': 10.0,
                    'amount': False
                }
            )]
        }

        self.contract.write({'state': 'open'})
        self.hr_payroll_new.create(test)

    def test_hr_payroll_news_without_employees(self):
        ids = self.payroll_new.employee_payroll_news_ids.ids
        with self.assertRaises(ValidationError):
            self.payroll_new.write({
                'employee_payroll_news_ids': [(2, r_id) for r_id in ids]
            })

    def test_hr_payroll_news_range_apply_one_employee(self):
        _ids = self.payroll_new.employee_payroll_news_ids.ids
        self.payroll_structure.write({
            'name': "Absenteeism Test",
            'date_range_apply': True
        })

        self.salary_rule_0.write({
            'name': 'VACACIONES HÁBILES',
            'constitutive': "is_const",
            'amount_select': "percentage",
            'amount_percentage_base': 130000,
            'condition_holiday': 'work_days',
        })

        self.payroll_new.write({
            'request_date_from': "2020-04-01",
            'request_date_to': "2020-04-07",
            'salary_rule_id': self.salary_rule_0.id
        })

        ids = [(4, r_id, False) for r_id in _ids]

        ids.append((0, 0, {
            'employee_id': self.employee.id,
            'payroll_news_id': False,
            'quantity': 2,
            'amount': 100
        }))
        self.payroll_new._compute_employee_count()
        with self.assertRaises(ValidationError):
            self.payroll_new.write({
                'name': "Validate Only one employee",
                'payroll_structure_id': self.payroll_structure.id,
                'salary_rule_id': self.salary_rule_0.id,
                'request_date_from': "2020-04-01",
                'request_date_to': "2020-04-07",
                'employee_payroll_news_ids': ids
            })

    def test_hr_payroll_news_range_date(self):
        with self.assertRaises(ValidationError):
            self.payroll_new.write({
                'date_end': "2020-04-01",
                'date_start': "2020-04-07",
            })

    def test_hr_payroll_news_onchange_request_date(self):

        self.payroll_structure.write({
            'name': "Absenteeism Test",
            'date_range_apply': True
        })

        self.salary_rule_0.write({
            'name': 'VACACIONES HÁBILES',
            'constitutive': "is_const",
            'amount_select': "percentage",
            'amount_percentage_base': 130000,
            'condition_holiday': 'work_days',
        })

        data = {
            'name': "Test Novelty",
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule_0.id,
            'request_date_from': "2020-04-01",
            'request_date_to': "2020-04-07",
            'employee_payroll_news_ids': [(0, 0, {
                'employee_id': self.employee.id,
                    'payroll_news_id': False,
                    'quantity': 2,
                    'amount': 100
                })
            ]
        }

        date_valid = self.hr_payroll_new.new(data)
        date_valid._onchange_request_date()

        data['request_date_from'] = '2020-04-10'
        date_invalid = self.hr_payroll_new.new(data)
        result = date_invalid._onchange_request_date()
        self.assertEqual(result, {})

    def test_onchange_range_work(self):
        self.payroll_structure.write({
            'name': "Absenteeism Test",
            'date_range_apply': True
        })

        self.salary_rule_0.write({
            'name': 'VACACIONES HÁBILES',
            'constitutive': "is_const",
            'amount_select': "percentage",
            'amount_percentage_base': 130000,
            'condition_holiday': 'work_days',
        })

        with self.assertRaises(ValidationError):
            result = self.payroll_new.write({
                'payroll_structure_id': self.payroll_structure.id,
                'salary_rule_id': self.salary_rule_0.id,
                'request_date_from': "2020-04-10",
                'request_date_to': "2020-04-07",
            })

        result = self.payroll_new.write({
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule_0.id,
            'request_date_from': "2020-04-01",
            'request_date_to': "2020-04-07",
        })

    def test_absenteeism_working(self):
        self.payroll_structure.write({
            'name': "Absenteeism Test",
            'date_range_apply': True
        })

        self.salary_rule_0.write({
            'name': 'VACACIONES HÁBILES',
            'constitutive': "is_const",
            'amount_select': "percentage",
            'amount_percentage_base': 130000,
            'condition_holiday': 'work_days',
        })

        self.payroll_new.write({
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule_0.id,
            'request_date_from': "2020-04-01",
            'request_date_to': "2020-04-07",
        })

        result = self.payroll_new._onchange_salary_rule_id()

    def test_compute_total_employee_payroll_news(self):
        self.hr_payroll_new.search([])._compute_total_employee_payroll_news()

    def test_action_add_employees(self):
        self.payroll_new.action_add_employees()

    def test_no_replicate_new_amount(self):
        payroll_new = self.hr_payroll_new.create({
            'name': "Test Novelty 2",
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule.id,
            'kanban_state': "done",
            'date_start': '2020-01-01',
            'date_end': '2020-01-31',
            'request_date_from': False,
            'request_date_to': False,
            'replicate_new': False,
            'check_create_replication': True,
            'stage_id': self.payrol_news_stage.id,
            'employee_payroll_news_ids': [(0, 0, {
                'employee_id': self.employee.id,
                'quantity': 2,
                'amount': 100
            })]
        })

    def test_replicate_new_amount(self):
        with self.assertRaises(ValidationError):
            payroll_new = self.hr_payroll_new.create({
                'name': "Test Novelty 3",
                'payroll_structure_id': self.payroll_structure.id,
                'salary_rule_id': self.salary_rule.id,
                'kanban_state': "done",
                'date_start': '2020-01-01',
                'date_end': '2020-01-31',
                'request_date_from': False,
                'request_date_to': False,
                'replicate_new': True,
                'check_create_replication': False,
                'stage_id': self.payrol_news_stage.id,
                'employee_payroll_news_ids': [(0, 0, {
                    'employee_id': self.employee.id,
                    'quantity': 2,
                    'amount': 100
                })]
            })
            payroll_new2 = self.hr_payroll_new.create({
                'name': "Test Novelty 4",
                'payroll_structure_id': self.payroll_structure.id,
                'salary_rule_id': self.salary_rule.id,
                'kanban_state': "done",
                'date_start': '2020-01-01',
                'date_end': '2020-05-18',
                'request_date_from': '2020-01-01',
                'request_date_to': '2020-01-31',
                'replicate_new': True,
                'check_create_replication': False,
                'stage_id': self.payrol_news_stage.id,
                'employee_payroll_news_ids': [(0, 0, {
                    'employee_id': self.employee.id,
                    'quantity': 2,
                    'amount': 100
                })]
            })

    def test_replicate_new_amount2(self):
        payroll_new = self.hr_payroll_new.create({
            'name': "Test Novelty 5",
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule.id,
            'kanban_state': "done",
            'date_start': '2020-01-01',
            'date_end': '2020-03-27',
            'request_date_from': False,
            'request_date_to': False,
            'replicate_new': True,
            'check_create_replication': False,
            'stage_id': self.payrol_news_stage.id,
            'employee_payroll_news_ids': [(0, 0, {
                'employee_id': self.employee.id,
                'quantity': 2,
                'amount': 100
            })]
        })
        payroll_new2 = self.hr_payroll_new.create({
            'name': "Test Novelty 6",
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule.id,
            'kanban_state': "done",
            'date_start': '2020-01-01',
            'date_end': '2020-03-27',
            'request_date_from': '2020-01-01',
            'request_date_to': '2020-03-27',
            'replicate_new': True,
            'check_create_replication': False,
            'stage_id': self.payrol_news_stage.id,
            'employee_payroll_news_ids': [(0, 0, {
                'employee_id': self.employee.id,
                'quantity': 2,
                'amount': 100
            })]
        })
        payroll_new3 = self.hr_payroll_new.create({
            'name': "Test Novelty 7",
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule.id,
            'kanban_state': "done",
            'date_start': date(2020, 1, 1),
            'date_end': '2020-03-27',
            'request_date_from': '2020-01-01',
            'request_date_to': '2020-03-27',
            'replicate_new': True,
            'check_create_replication': False,
            'stage_id': self.payrol_news_stage.id,
            'employee_payroll_news_ids': [(0, 0, {
                'employee_id': self.employee.id,
                'quantity': 2,
                'amount': 100
            })]
        })
