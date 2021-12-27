from datetime import date, datetime, timedelta
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import logging


class TestBitsHrPayrollNews(TransactionCase):

    def setUp(self):
        super(TestBitsHrPayrollNews, self).setUp()
        self.hr_employee = self.env['hr.employee']
        self.hr_payroll_structure = self.env['hr.payroll.structure']
        self.hr_payslip_employees = self.env['hr.payslip.employees']
        self.hr_payslip_dian_detail_line = self.env['hr.payslip.dian.detail.line']
        self.hr_payslip_dian_detail = self.env['hr.payslip.dian.detail']
        self.hr_employee_payroll_news = self.env['hr.employee.payroll.news']
        self.hr_salary_rule = self.env['hr.salary.rule']
        self.hr_payroll_news_stage = self.env['hr.payroll.news.stage']
        self.hr_payroll_new = self.env['hr.payroll.news']
        self.hr_payroll_structure_type = self.env['hr.payroll.structure.type']
        self.hr_salary_rule = self.env['hr.salary.rule']
        self.hr_salary_rule_category = self.env['hr.salary.rule.category']
        self.hr_contract = self.env['hr.contract']
        self.hr_payslip = self.env['hr.payslip']
        self.hr_payslip_run = self.env['hr.payslip.run']
        self.payment_method = self.env['payment.method']
        self.payment_way = self.env['payment.way']
        self.payrol_news_stage = self.hr_payroll_news_stage.create({
            'name': "Stage Test"
        })

        self.payment_way_1 = self.payment_way.create({
            'name': 'TEST code Payment way',
            'code': 'code payment way'
        })
        self.payment_method_1 = self.payment_method.create({
            'name': 'TEST code Payment method',
            'code': 'code payment method'
        })

        self.salary_structure = self.env.ref(
            'bits_hr_payroll_news.hr_payroll_structure_type_employee_01')

        config = self.env['res.config.settings'].create({})
        config.module_bits_hr_contract_advance = True
        config.execute()

        self.contract = self.hr_contract.create({
            'name': "Contract Test",
            'rate': 4.3500,
            'date_start': datetime.now(),
            'date_end': datetime.now()+timedelta(days=365),
            'structure_type_id': self.salary_structure.id,
            'wage': 800000
        })
        self.employee = self.hr_employee.create({
            'name': "Test Payroll News",
            'names': "Test Payroll news complete",
            'surnames': "Test Payroll news surnames",
            'known_as': "Test Payroll news know_as",
            'contract_id': self.contract.id,
            'document_type': '13',
            'identification_id': "75395146"
        })
        self.structure_type = self.hr_payroll_structure_type.create({
            'name': "Test Type",
            'wage_type': "monthly",
            'is_novelty': True
        })
        self.payroll_structure = self.hr_payroll_structure.create({
            'name': "Structure Test",
            'type_id': self.structure_type.id
        })
        self.salary_rule_category = self.hr_salary_rule_category.create({
            'name': "Salary Category Test",
            'code': "SCT"
        })
        self.salary_rule = self.hr_salary_rule.create({
            'name': "Test Rule",
            'code': "ICO",
            'sequence': 100,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1.0,
            'constitutive': "is_const"
        })
        self.salary_rule_inco = self.hr_salary_rule.create({
            'name': "Test Rule",
            'code': "INCO",
            'sequence': 100,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1.0,
            'constitutive': "is_const"
        })
        self.salary_rule_0 = self.hr_salary_rule.create({
            'name': "Test Rule 0",
            'code': "TSTR0",
            'sequence': 10,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "range",
            'benefit_calculate': 'rem_work_days',
            'condition_range_min': 50,
            'condition_range_max': 1000,
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1.0
        })
        self.salary_rule_1 = self.hr_salary_rule.create({
            'name': "Test Rule 1",
            'code': "TSTR1",
            'sequence': 101,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'affect_worked_days': True,
            'quantity': 2.0
        })
        self.salary_rule_2 = self.hr_salary_rule.create({
            'name': "Test Rule 2",
            'code': "TSTR2",
            'sequence': 102,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'affect_worked_days': True,
            'quantity': -2.0
        })
        self.salary_rule_3 = self.hr_salary_rule.create({
            'name': "Test Rule 3",
            'code': "TSTR3",
            'sequence': 103,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'benefit_calculate': 'rem_work_days',
            'quantity': 2.0
        })
        self.salary_rule_4 = self.hr_salary_rule.create({
            'name': "Test Rule 4",
            'code': "TSTR4",
            'sequence': 104,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'constitutive_calculate': True,
            'quantity': 2.0
        })
        self.salary_rule_5 = self.hr_salary_rule.create({
            'name': "Test Rule 5",
            'code': "TSTR5",
            'sequence': 105,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'constitutive_calculate': True,
            'quantity': 2.0,
            'amount_select': "percentage",
            'amount_percentage': 0.0,
            'amount_percentage_base': "contract.wage"
        })
        self.salary_rule_6 = self.hr_salary_rule.create({
            'name': "Test Rule 6",
            'code': "TSTR6",
            'sequence': 106,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'affect_payslip': False,
            'constitutive_calculate': True,
            'quantity': 0.0,
            'amount_select': "percentage",
            'amount_percentage': 0.0,
            'amount_percentage_base': "2 * 980000"
        })
        self.salary_rule_arl = self.hr_salary_rule.create({
            'name': 'ARL',
            'code': 'ARL',
            'sequence': 300,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'affect_payslip': False,
            'constitutive_calculate': True,
            'quantity': 1.0,
            'amount_select': "percentage",
            'amount_percentage': 0.0,
            'amount_percentage_base': "contract.wage"
        })

        self.salary_rule_ibc_suma = self.hr_salary_rule.create({
            'name': 'Suma IBC',
            'code': 'suma-ibc',
            'sequence': 5,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'quantity': '1.0',
            'amount_select': 'percentage',
            'amount_percentage_base': '0',
            'apply_other_rules': 'TSTR4,TSTR5',
            'apply_in': 'total',
            'constitutive_percentage': 100.0000,
            'amount_percentage': 100.0000,
        })

        self.salary_rule_ibc_suma_2 = self.hr_salary_rule.create({
            'name': 'Suma IBC',
            'code': 'suma-ibc-2',
            'sequence': 5,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'quantity': '1.0',
            'amount_select': 'percentage',
            'amount_percentage_base': '0',
            'apply_other_rules': 'TSTR4,TSTR5',
            'apply_in': 'total',
            'constitutive_percentage': 100.0000,
            'amount_percentage': 100.0000,
        })

        self.salary_rule_ibc_resta = self.hr_salary_rule.create({
            'name': 'Suma IBC',
            'code': 'resta-ibc',
            'sequence': 5,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'quantity': '1.0',
            'amount_select': 'percentage',
            'amount_percentage_base': '0',
            'apply_other_rules': 'TSTR4,TSTR5',
            'apply_in': 'amount',
            'constitutive_percentage': 100.0000,
            'amount_percentage': 100.0000,
        })

        self.payroll_new = self.hr_payroll_new.create({
            'name': "Test Novelty",
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule.id,
            'stage_id': self.payrol_news_stage.id,
            'employee_payroll_news_ids': [
                [
                    0,
                    0,
                    {
                        'payroll_news_id': False,
                        'quantity': 1,
                        'employee_id': self.employee.id,
                        'amount': 20
                    }
                ]
            ]
        })
        self.payroll_new_inco = self.hr_payroll_new.create({
            'name': "Test Novelty",
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule_inco.id,
            'stage_id': self.payrol_news_stage.id,
            'employee_payroll_news_ids': [
                [
                    0,
                    0,
                    {
                        'payroll_news_id': False,
                        'quantity': 1,
                        'employee_id': self.employee.id,
                        'amount': 20
                    }
                ]
            ]
        })
        self.employee_payroll = self.hr_employee_payroll_news.create({
            'employee_id': self.employee.id,
            'quantity': 2,
            'amount': 100,
            'payroll_news_id': self.payroll_new.id
        })
        self.employee_payroll_inco = self.hr_employee_payroll_news.create({
            'employee_id': self.employee.id,
            'quantity': 2,
            'amount': 100,
            'payroll_news_id': self.payroll_new_inco.id
        })
        self.payslip = self.hr_payslip.create({
            'name': "Payroll Test",
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'struct_id': self.payroll_structure.id,
            'date_from': datetime.now(),
            'date_to': datetime.now()+timedelta(days=365)
        })
        self.env['decimal.precision'].create({
            'name': 'PAYROLLTEST',
            'digits': 2,
        })
        
        self.hr_payslip_employees_1 = self.hr_payslip_employees.create({
            'display_name': 'TEST EMPLOYEES 1',
            'structure_id': self.payroll_structure.id,
            'employee_ids': [(0, 0, {
                'name': "Test Payroll News",
                'names': "Test Payroll news complete",
                'surnames': "Test Payroll news surnames",
                'known_as': "Test Payroll news know_as",
                'contract_id': self.contract.id,
                'document_type': '13',
                'identification_id': "222222222"
            })]
        })

        datetime_last = datetime.now()+timedelta(days=365)
        self.hr_payslip_run_1 = self.hr_payslip_run.create({
            'name': 'Test Paylsip 1',
            'date_start': datetime.now().date(),
            'date_end': datetime_last.date(),
            'payment_method_id': self.payment_method_1.id,
            'payment_way_id': self.payment_way_1.id,
            'payment_date': datetime.now().date()
        })


        self.hr_payslip_dian_detail_1 = self.hr_payslip_dian_detail.create({

            'request_date': datetime.now().date(),
            'code': 'A1',
            'line_ids':  [(0, 0, {
                'number': "Test Payroll News",
                'status': "Test Payroll news complete"
            })]
        })

        self.hr_payslip_dian_detail_2 = self.hr_payslip_dian_detail.create({

            'request_date': datetime.now().date(),
            'code': 'A1',
            'line_ids': False
        })

    
    def test_get_general_status(self):
        self.hr_payslip_dian_detail_1._get_general_status()
    
    def test_get_general_status_no_lines(self):
        self.hr_payslip_dian_detail_2._get_general_status()
    
    def test_get_general_status_create_date(self):
        self.hr_payslip_dian_detail_1.write({
            'line_ids':  [(0, 0, {
                'create_date': datetime.now().date(),
                'number': "Test Payroll News",
                'status': "Test Payroll news complete"
            })]
        })

        self.hr_payslip_dian_detail_1._get_general_status()
