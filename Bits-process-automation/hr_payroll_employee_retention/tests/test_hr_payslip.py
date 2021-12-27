from datetime import datetime, timedelta, date
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError, UserError


class TestHrPayslip(TransactionCase):

    def setUp(self):
        super(TestHrPayslip, self).setUp()
        self.hr_employee = self.env['hr.employee']
        self.hr_payroll_structure = self.env['hr.payroll.structure']
        self.hr_employee_payroll_news = self.env['hr.employee.payroll.news']
        self.hr_salary_rule = self.env['hr.salary.rule']
        self.hr_payroll_news_stage = self.env['hr.payroll.news.stage']
        self.hr_payroll_new = self.env['hr.payroll.news']
        self.hr_payroll_structure_type = self.env['hr.payroll.structure.type']
        self.hr_salary_rule = self.env['hr.salary.rule']
        self.hr_salary_rule_category = self.env['hr.salary.rule.category']
        self.hr_contract = self.env['hr.contract']
        self.hr_payslip = self.env['hr.payslip']
        self.config_settings = self.env['res.config.settings']
        self.hr_work_entry_type = self.env['hr.work.entry.type']
        self.hr_parameter_retention = self.env[
            'hr.payroll.parameter.retention']
        self.hr_payroll_retention = self.env['hr.payroll.retention']
        self.employee_retention = self.env['hr.payroll.employee.retention']
        self.document_type = self.env['hr.employee.document.type']
        self.employee_document_line = self.env['hr.employee.document.line']

        self.HrPayrollHolidayLapse = self.env['hr.payroll.holiday.lapse']

        self.salary_rule_0 = self.hr_salary_rule.search(
            [('code', '=', 'BASIC')], limit=1)
        self.salary_rule_1 = self.hr_salary_rule.search(
            [('code', '=', '15')], limit=1)
        self.salary_rule_2 = self.hr_salary_rule.search(
            [('code', '=', '20')], limit=1)
        self.salary_rule_3 = self.hr_salary_rule.search(
            [('code', '=', '25')], limit=1)
        self.salary_rule_4 = self.hr_salary_rule.search(
            [('code', '=', '120')], limit=1)
        self.salary_rule_5 = self.hr_salary_rule.search(
            [('code', '=', '237')], limit=1)
        self.salary_rule_6 = self.hr_salary_rule.search(
            [('code', '=', '239')], limit=1)
        self.salary_rule_7 = self.hr_salary_rule.search(
            [('code', '=', '285')], limit=1)
        self.salary_rule_8 = self.hr_salary_rule.search(
            [('code', '=', '3020')], limit=1)
        self.salary_rule_9 = self.hr_salary_rule.search(
            [('code', '=', '3023')], limit=1)
        self.salary_rule_10 = self.hr_salary_rule.search(
            [('code', '=', '3010')], limit=1)
        self.salary_rule_11 = self.hr_salary_rule.search(
            [('code', '=', '3026')], limit=1)
        self.salary_rule_12 = self.hr_salary_rule.search(
            [('code', '=', '3031')], limit=1)
        self.salary_rule_13 = self.hr_salary_rule.search(
            [('code', '=', '26')], limit=1)
        self.salary_rule_14 = self.hr_salary_rule.search(
            [('code', '=', '27')], limit=1)
        # self.salary_rule_13, self.salary_rule_14 = \
        #     self.hr_salary_rule.search([('code', '=', '26')], limit=2)
        self.salary_rule_15 = self.hr_salary_rule.search(
            [('code', '=', '145')], limit=1
        )
        self.salary_rule_16 = self.hr_salary_rule.search(
            [('code', '=', '146')], limit=1
        )
        self.salary_rule_17 = self.hr_salary_rule.search(
            [('code', '=', '4')], limit=1
        )
        self.salary_rule_18 = self.hr_salary_rule.search(
            [('code', '=', '5')], limit=1
        )
        self.salary_rule_19 = self.hr_salary_rule.search(
            [('code', '=', '60')], limit=1
        )
        self.salary_rule_20 = self.hr_salary_rule.search(
            [('code', '=', '65')], limit=1
        )
        self.salary_rule_21 = self.hr_salary_rule.search(
            [('code', '=', '70')], limit=1
        )
        self.salary_rule_22 = self.hr_salary_rule.search(
            [('code', '=', '75')], limit=1
        )

        self.document_type_1 = self.document_type.create({
            'name': "Document 1",
            'code': "DOC1"
        })
        self.document_type_2 = self.document_type.create({
            'name': "Document 2",
            'code': "DOC2"
        })
        self.document_type_3 = self.document_type.create({
            'name': "Document 3",
            'code': "DOC3"
        })
        self.document_type_4 = self.document_type.create({
            'name': "Document 4",
            'code': "PAD"
        })
        self.document_type_5 = self.document_type.create({
            'name': "Document 5",
            'code': "INV"
        })

        self.payroll_retention_1 = self.hr_payroll_retention.create({
            'name': "Retencion en Rentas de Trabajo",
            'code': "1",
            'line_ids': [(0, 0, {
                'code': 'BASIC',
                'name': "Line 1",
                'salary_rule_ids': [(6, 0, [self.salary_rule_0.id,
                                            self.salary_rule_1.id,
                                            self.salary_rule_2.id,
                                            self.salary_rule_3.id,
                                            self.salary_rule_13.id,
                                            self.salary_rule_14.id,
                                            self.salary_rule_15.id,
                                            self.salary_rule_16.id,
                                            self.salary_rule_17.id,
                                            self.salary_rule_18.id,
                                            self.salary_rule_19.id,
                                            self.salary_rule_20.id,
                                            self.salary_rule_21.id,
                                            self.salary_rule_22.id,
                                            self.salary_rule_4.id])],
                'maximum_percentage':0,
                'uvt_maximum':0
            }), (0, 0, {
                'code': 'BONUSES',
                'name': "Line 2",
                'salary_rule_ids': [(6, 0, [self.salary_rule_5.id,
                                            self.salary_rule_6.id,
                                            self.salary_rule_7.id])],
                'maximum_percentage':0,
                'uvt_maximum':0
            }), (0, 0, {
                'code': 'BOND',
                'name': 'Bono',
                'salary_rule_ids': [],
                'maximum_percentage':0,
                'uvt_maximum':0
            }), (0, 0, {
                'code': 'VLN_CONTRIBUTION',
                'name': 'Aporte Voluntario Fondo de Pensiones Empleador',
                'salary_rule_ids': [],
                'maximum_percentage':0,
                'uvt_maximum':0
            })]
        })

        self.payroll_retention_2 = self.hr_payroll_retention.create({
            'name': "Ingresos no Constitutivos de Renta",
            'code': "2",
            'line_ids': [(0, 0, {
                'code': '3020',
                'name': "Line 1",
                'salary_rule_ids': [(6, 0, [self.salary_rule_8.id])],
                'maximum_percentage':0,
                'uvt_maximum':0
            }), (0, 0, {
                'code': '3023',
                'name': "Line 2",
                'salary_rule_ids': [(6, 0, [self.salary_rule_9.id])],
                'maximum_percentage':0,
                'uvt_maximum':0
            }), (0, 0, {
                'code': '3010',
                'name': "Line 3",
                'salary_rule_ids': [(6, 0, [self.salary_rule_10.id])],
                'maximum_percentage':0,
                'uvt_maximum':0
            }), (0, 0, {
                'code': 'VLN_CNTR_PENSION_FUND',
                'name': 'Aptes vlnt a fondo de Pensiones obligatorias.',
                'salary_rule_ids': [],
                'maximum_percentage':0,
                'uvt_maximum':0
            }), (0, 0, {
                'code': 'OTH_INC_NOT_CONSTITUTING_INC',
                'name': 'Otros ingresos no constitutivos de renta',
                'salary_rule_ids': [],
                'maximum_percentage':0,
                'uvt_maximum':0
            })]
        })

        self.payroll_retention_3 = self.hr_payroll_retention.create({
            'name': "Deducciones",
            'code': "3",
            'line_ids': [(0, 0, {
                'code': 'HOUSING_INTERESTS',
                'name': "Line 1",
                'salary_rule_ids': [],
                'maximum_percentage':0,
                'uvt_maximum':100,
                'document_code':"DOC1",
                'document_code': 'INV'
            }), (0, 0, {
                'code': 'DEPENDENT_PAYMENTS',
                'name': "Line 2",
                'salary_rule_ids': [],
                'maximum_percentage':10,
                'uvt_maximum':32,
                'document_code': 'PAD'
            }), (0, 0, {
                'code': 'PREPAID_MEDICINE_PAYMENTS',
                'name': "Line 3",
                'salary_rule_ids': [],
                'maximum_percentage':0,
                'uvt_maximum':16,
                'document_code': 'PSMP'
            })]
        })

        self.payroll_retention_4 = self.hr_payroll_retention.create({
            'name': "Rentas Exentas",
            'code': "4",
            'line_ids': [(0, 0, {
                'code': '3026',
                'name': "Line 1",
                'salary_rule_ids': [(6, 0, [self.salary_rule_11.id])],
                'maximum_percentage': 30,
                'uvt_maximum': 3800
            }), (0, 0, {
                'code': '3031',
                'name': "Line 2",
                'salary_rule_ids': [(6, 0, [self.salary_rule_12.id])],
                'maximum_percentage': 30,
                'uvt_maximum': 3800
            }), (0, 0, {
                'code': 'OTHER_RENTALS',
                'name': 'Otros rentas exentas',
                'salary_rule_ids': [],
                'maximum_percentage':0,
                'uvt_maximum':0
            })
            ]
        })

        self.payroll_retention_5 = self.hr_payroll_retention.create({
            'name': ("Renta de Trabajo Exenta (25%). Maximo $ 8.224.800 "
                     "Año 2019. (240 Uvt)"),
            'code': "5",
            'line_ids': [(0, 0, {
                'code': 'EXEMPT_WORK_INCOME',
                'name': "Line 1",
                'maximum_percentage': 25,
                'uvt_maximum': 240
            })]
        })
        self.employee = self.hr_employee.create({
            'name': "Juan Perez",
            'names': "Juan Perez",
            'surnames': "Perez",
            'known_as': "Perez",
            'document_type': "12",
            'identification_id': "1597534563"
        })
        self.employee_document_line.create({
            'employee_id': self.employee.id,
            'document_type_id': self.document_type_1.id,
            'amount_contributibe': 100000

        })
        self.employee_document_line.create({
            'employee_id': self.employee.id,
            'document_type_id': self.document_type_2.id,
            'amount_contributibe': 100000

        })
        self.employee_document_line.create({
            'employee_id': self.employee.id,
            'document_type_id': self.document_type_3.id,
            'amount_contributibe': 100000

        })
        self.employee_1 = self.hr_employee.create({
            'name': "Mario Perez",
            'names': "Mario Perez",
            'surnames': "Perez",
            'known_as': "Perez",
            'document_type': "12",
            'identification_id': "3571594569"

        })
        self.employee_document_line.create({
            'employee_id': self.employee_1.id,
            'document_type_id': self.document_type_1.id,
            'amount_contributibe': 100000

        })
        self.employee_document_line.create({
            'employee_id': self.employee_1.id,
            'document_type_id': self.document_type_2.id,
            'amount_contributibe': 100000

        })
        self.employee_document_line.create({
            'employee_id': self.employee_1.id,
            'document_type_id': self.document_type_3.id,
            'amount_contributibe': 100000

        })

        self.work_entry_type = self.env.ref(
            'hr_work_entry.work_entry_type_attendance')

        self.work_entry_type_01 = self.hr_work_entry_type.create({
            'name': 'Entry Type Test',
            'code': 'TST100',
            'round_days': 'NO'
        })

        self.salary_structure = self.env.ref(
            'bits_hr_payroll_news.hr_payroll_structure_employee_01')

        self.salary_structure_type = self.env.ref(
            'bits_hr_payroll_news.hr_payroll_structure_type_employee_01')

        self.contract = self.hr_contract.create({
            'name': "Test Contract",
            'structure_type_id': self.salary_structure_type.id,
            'employee_id': self.employee.id,
            'date_start': date(2020, 1, 1),
            'wage_type': "monthly",
            'wage': 5800000,
            'state': 'open',
            'rate': 0.5220
        })

        self.contract_1 = self.hr_contract.create({
            'name': "Test Contract",
            'structure_type_id': self.salary_structure_type.id,
            'employee_id': self.employee_1.id,
            'date_start': date(2020, 1, 1),
            'wage_type': "monthly",
            'wage': 2000000,
            'state': 'open',
            'rate': 0.5220
        })

        self.payslip = self.hr_payslip.create({
            'name': "Payroll Test",
            'date_from': date(2020, 1, 1),
            'date_to': date(2020, 1, 31),
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'struct_id': self.salary_structure.id,
            'worked_days_line_ids': [(0, 0, {
                'work_entry_type_id': self.work_entry_type.id,
                'number_of_days': 30,
                'amount': 5800000
            })]
        })

        self.payslip_1 = self.hr_payslip.create({
            'name': "Payroll Test",
            'date_from': date(2020, 1, 1),
            'date_to': date(2020, 1, 31),
            'employee_id': self.employee_1.id,
            'contract_id': self.contract_1.id,
            'struct_id': self.salary_structure.id,
            'worked_days_line_ids': [(0, 0, {
                'work_entry_type_id': self.work_entry_type.id,
                'number_of_days': 30,
                'amount': 200000
            })]
        })

    def test_compute_sheet(self):
        with self.assertRaises(UserError):
            self.payslip.compute_sheet()

    def test_compute_sheet_config(self):
        parameter_retention = self.hr_parameter_retention.search(
            [('year', '=', 2020)])
        self.env['ir.config_parameter'].sudo().set_param(
            'hr_payroll.parameter_retention_id', parameter_retention.id)
        self.payslip.compute_sheet()

    def test_compute_sheet_retention_zero(self):
        parameter_retention = self.hr_parameter_retention.search(
            [('year', '=', 2020)])
        self.env['ir.config_parameter'].sudo().set_param(
            'hr_payroll.parameter_retention_id', parameter_retention.id)
        self.payslip_1.compute_sheet()

    def test_additional_calculations_exempt_income(self):
        self.payroll_retention_4.unlink()
        parameter_retention = self.hr_parameter_retention.search(
            [('year', '=', 2020)])
        self.env['ir.config_parameter'].sudo().set_param(
            'hr_payroll.parameter_retention_id', parameter_retention.id)
        payroll_retention_4 = self.hr_payroll_retention.create({
            'name': "Rentas Exentas",
            'code': "4",
            'line_ids': [(0, 0, {
                'name': "Line 1",
                'salary_rule_ids': [(6, 0, [self.salary_rule_11.id])],
                'maximum_percentage':30,
                'uvt_maximum':0
            }), (0, 0, {
                'name': "Line 2",
                'salary_rule_ids': [(6, 0, [self.salary_rule_12.id])],
                'maximum_percentage':0,
                'uvt_maximum':3800
            }), (0, 0, {
                'code': 'OTHER_RENTALS',
                'name': 'Otros rentas exentas',
                'salary_rule_ids': [(6, 0, [self.salary_rule_9.id])],
                'maximum_percentage':12
            })]
        })
        self.payslip_1.compute_sheet()

    def test_additional_calculations_exempt_income_other(self):
        self.payroll_retention_4.unlink()
        parameter_retention = self.hr_parameter_retention.search(
            [('year', '=', 2020)])
        self.env['ir.config_parameter'].sudo().set_param(
            'hr_payroll.parameter_retention_id', parameter_retention.id)
        payroll_retention_4 = self.hr_payroll_retention.create({
            'name': "Rentas Exentas",
            'code': "4",
            'line_ids': [(0, 0, {
                'name': "Line 1",
                'salary_rule_ids': [(6, 0, [self.salary_rule_12.id,
                                            self.salary_rule_11.id,
                                            self.salary_rule_9.id])],
                'maximum_percentage':1,
                'uvt_maximum':3800
            }), (0, 0, {
                'name': "Line 2",
                'salary_rule_ids': [(6, 0, [])],
                'maximum_percentage':30,
                'uvt_maximum':0
            }), (0, 0, {
                'code': 'OTHER_RENTALS',
                'name': 'Otros rentas exentas',
                'salary_rule_ids': [(6, 0, [self.salary_rule_9.id])]
            })
            ]
        })
        self.payslip_1.compute_sheet()

    def test_payroll_config_set_values(self):
        config_sttings = self.config_settings.create({
            'date_truncate': date(2020, 1, 1),
            'date_execute': date(2020, 1, 1)
        })
        config_sttings.set_values()
        self.employee_retention._cron_execute_employee_retentions()

    def test_payroll_config_set_values_without_info(self):
        config_sttings = self.config_settings.create({
        })
        config_sttings.set_values()

    def test_get_dafault_country(self):
        self.hr_parameter_retention._get_dafault_country()
        self.hr_parameter_retention._get_dafault_currency()

    def test_cron_execute_employee_retentions(self):
        self.employee_retention._cron_execute_employee_retentions()

    def test_cron_execute_employee_retentions_now_date(self):
        self.config_settings.create({
            'date_truncate': date(2020, 1, 1),
            'date_execute': datetime.today().date()
        })
        self.env['ir.config_parameter'].sudo().set_param(
            'str_date_truncate', date(2020, 1, 1))
        self.env['ir.config_parameter'].sudo().set_param(
            'str_date_exec', datetime.today().date())
        self.employee_retention._cron_execute_employee_retentions()

    def test_discount_dependent(self):
        parameter_retention = self.hr_parameter_retention.search(
            [('year', '=', 2020)])
        self.env['ir.config_parameter'].sudo().set_param(
            'hr_payroll.parameter_retention_id', parameter_retention.id)
        self.employee_1.write({
            "documents_employee_ids": [
                (0, 0, {
                    "document_type_id": self.document_type_4.id,
                    "amount_contributibe": 0,
                    "expiration_date": date(2020, 1, 17),
                    "state": "enabled"
                }),
                (0, 0, {
                    "document_type_id": self.document_type_5.id,
                    "amount_contributibe": 0,
                    "expiration_date": date(2020, 1, 17),
                    "state": "enabled"
                })
            ]
        })
        payslip = self.hr_payslip.create({
            'name': "Payroll Test",
            'date_from': date(2020, 1, 1),
            'date_to': date(2020, 1, 31),
            'employee_id': self.employee_1.id,
            'contract_id': self.contract_1.id,
            'struct_id': self.salary_structure.id,
            'worked_days_line_ids': [(0, 0, {
                'work_entry_type_id': self.work_entry_type.id,
                'number_of_days': 30,
                'amount': 200000
            })]
        })
        payslip.compute_sheet()

    def test_discount_dependent_withoutuvt(self):
        parameter_retention = self.hr_parameter_retention.search(
            [('year', '=', 2020)])
        self.env['ir.config_parameter'].sudo().set_param(
            'hr_payroll.parameter_retention_id', parameter_retention.id)
        pad_deduction = self.env["hr.payroll.retention.line"].search([
            ('document_code', '=', 'PAD')
        ])
        pad_deduction.write({
            'uvt_maximum': 0
        })
        self.employee_1.write({
            "documents_employee_ids": [
                (0, 0, {
                    "document_type_id": self.document_type_4.id,
                    "amount_contributibe": 0,
                    "expiration_date": date(2020, 1, 17),
                    "state": "enabled"
                }),
                (0, 0, {
                    "document_type_id": self.document_type_5.id,
                    "amount_contributibe": 0,
                    "expiration_date": date(2020, 1, 17),
                    "state": "enabled"
                })
            ]
        })
        payslip = self.hr_payslip.create({
            'name': "Payroll Test",
            'date_from': date(2020, 1, 1),
            'date_to': date(2020, 1, 31),
            'employee_id': self.employee_1.id,
            'contract_id': self.contract_1.id,
            'struct_id': self.salary_structure.id,
            'worked_days_line_ids': [(0, 0, {
                'work_entry_type_id': self.work_entry_type.id,
                'number_of_days': 30,
                'amount': 200000
            })]
        })
        payslip.compute_sheet()

    def test_discount_dependent_disabled(self):
        parameter_retention = self.hr_parameter_retention.search(
            [('year', '=', 2020)])
        self.env['ir.config_parameter'].sudo().set_param(
            'hr_payroll.parameter_retention_id', parameter_retention.id)
        self.employee_1.write({
            "documents_employee_ids": [
                (0, 0, {
                    "document_type_id": self.document_type_4.id,
                    "amount_contributibe": 0,
                    "expiration_date": date(2020, 1, 17),
                    "state": "disabled"
                }),
                (0, 0, {
                    "document_type_id": self.document_type_5.id,
                    "amount_contributibe": 0,
                    "expiration_date": date(2020, 1, 17),
                    "state": "enabled"
                })
            ]
        })
        payslip = self.hr_payslip.create({
            'name': "Payroll Test",
            'date_from': date(2020, 1, 1),
            'date_to': date(2020, 1, 31),
            'employee_id': self.employee_1.id,
            'contract_id': self.contract_1.id,
            'struct_id': self.salary_structure.id,
            'worked_days_line_ids': [(0, 0, {
                'work_entry_type_id': self.work_entry_type.id,
                'number_of_days': 30,
                'amount': 200000
            })]
        })
        payslip.compute_sheet()

    def test_liquidation_apportionment(self):
        self.HrPayrollHolidayLapse.create(
            {
                'name': ' ',
                'begin_date': datetime.strftime(
                    datetime.now() - timedelta(367), '%Y-%m-%d'
                ),
                'end_date': datetime.strftime(
                    datetime.now() - timedelta(2), '%Y-%m-%d'
                ),
                'employee_id': self.employee_1.id,
                'type_vacation': 'normal',
                'state': '1',
            }
        )
        parameter_retention = self.hr_parameter_retention.search(
            [('year', '=', 2020)])
        self.env['ir.config_parameter'].sudo().set_param(
            'hr_payroll.parameter_retention_id', parameter_retention.id)
        structure_type = self.hr_payroll_structure_type.create({
            "name": "Liquidación"
        })
        struct = self.hr_payroll_structure.create({
            "name": "Liquidación general normal",
            "type_id": structure_type.id
        })
        payslip = self.hr_payslip.create({
            'name': "Payroll Test",
            'date_from': date(2020, 1, 1),
            'date_to': date(2020, 1, 29),
            'employee_id': self.employee_1.id,
            'contract_id': self.contract_1.id,
            'struct_id': struct.id,
            'worked_days_line_ids': [(0, 0, {
                'work_entry_type_id': self.work_entry_type.id,
                'number_of_days': 29,
                'amount': 8000000
            })]
        })
        payslip.compute_sheet()

    def test_retention(self):
        parameter_retention = self.hr_parameter_retention.search(
            [('year', '=', 2020)])
        self.env['ir.config_parameter'].sudo().set_param(
            'hr_payroll.parameter_retention_id', parameter_retention.id)
        structure_type = self.hr_payroll_structure_type.create({
            "name": "Liquidación"
        })
        struct = self.hr_payroll_structure.create({
            "name": "Liquidación general normal",
            "type_id": structure_type.id
        })
        payslip = self.hr_payslip.create({
            'name': "Payroll Test",
            'date_from': date(2020, 1, 1),
            'date_to': date(2020, 1, 15),
            'employee_id': self.employee_1.id,
            'contract_id': self.contract_1.id,
            'struct_id': struct.id,
            'worked_days_line_ids': [(0, 0, {
                'work_entry_type_id': self.work_entry_type.id,
                'number_of_days': 15,
                'amount': 8000000
            })]
        })
        payslip.compute_sheet()

        payslip2 = self.hr_payslip.create({
            'name': "Payroll Test",
            'date_from': date(2020, 1, 16),
            'date_to': date(2020, 1, 31),
            'employee_id': self.employee_1.id,
            'contract_id': self.contract_1.id,
            'struct_id': struct.id,
            'worked_days_line_ids': [(0, 0, {
                'work_entry_type_id': self.work_entry_type.id,
                'number_of_days': 16,
                'amount': 8000000
            })]
        })
        payslip2.compute_sheet()

    def test_retention_zero(self):
        parameter_retention = self.hr_parameter_retention.search(
            [('year', '=', 2020)])
        self.env['ir.config_parameter'].sudo().set_param(
            'hr_payroll.parameter_retention_id', parameter_retention.id)
        structure_type = self.hr_payroll_structure_type.create({
            "name": "Liquidación"
        })
        struct = self.hr_payroll_structure.create({
            "name": "Liquidación general normal",
            "type_id": structure_type.id
        })
        payslip = self.hr_payslip.create({
            'name': "Payroll Test",
            'date_from': date(2020, 1, 1),
            'date_to': date(2020, 1, 15),
            'employee_id': self.employee_1.id,
            'contract_id': self.contract_1.id,
            'struct_id': struct.id,
            'worked_days_line_ids': [(0, 0, {
                'work_entry_type_id': self.work_entry_type.id,
                'number_of_days': 15,
                'amount': 0
            })]
        })
        payslip.compute_sheet()
