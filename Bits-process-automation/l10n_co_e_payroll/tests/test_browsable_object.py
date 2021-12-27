# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from pytz import timezone
from datetime import datetime, timedelta, date
import logging
from ..models.browsable_object import Payslips


class TestEPayroll(TransactionCase):

    def setUp(self):
        super(TestEPayroll, self).setUp()
        self.social_security = self.env['social.security']
        self.hr_contract = self.env['hr.contract']
        self.hr_payslip = self.env['hr.payslip']
        self.res_partner = self.env['res.partner']
        self.hr_employee = self.env['hr.employee']
        self.hr_salary_rule = self.env['hr.salary.rule']
        self.hr_payroll_structure = self.env['hr.payroll.structure']
        self.hr_payroll_structure_type = self.env['hr.payroll.structure.type']
        self.hr_salary_rule_category = self.env['hr.salary.rule.category']
        self.tech_provider = self.env['l10n_co.tech.provider']
        self.settlement_ref = self.env['settlement.history']
        self.ir_sequence = self.env['ir.sequence']
        self.hr_payslip_line = ['hr.payslip.line']

        self.ir_sequence_1 = self.ir_sequence.create({
            'name': "Test sequence_1",
            'padding': 1,
            'number_increment': 1,
            'prefix': "PRE",
            'suffix': "SU",
            'number_next': 1
        })

        new_social_security = self.social_security.create({
            'code': 'TST001',
            'name': 'Prueba de Ingreso de datos',
            'entity_type': 'arl'
        })

        self.termination = self.ref(
            'hr_payroll_settlement.reason_dsjc_nor')

        self.tech_provider_1 = self.env.ref(
            'l10n_co_tech_provider_payroll.l10n_co_tech_provider_payroll_01')

        self.salary_rule_category = self.hr_salary_rule_category.create({
            'name': "Salary Category Test",
            'code': "SCT"
        })

        self.structure_type = self.hr_payroll_structure_type.create({
            'name': "Test Type",
            'wage_type': "monthly"
        })

        self.contract = self.hr_contract.create({
            'name': "Contract Test",
            'date_start': datetime.now(),
            'date_end': datetime.now()+timedelta(days=365),
            'wage': 3150000,
            'structure_type_id': self.structure_type.id,
            'high_risk_pension': True,
        })

        self.contract_id = self.hr_contract.create({
            'name': "Contract Test 2",
            'date_start': datetime.now(),
            'date_end': datetime.now()+timedelta(days=365),
            'wage': 3150000,
            'structure_type_id': self.structure_type.id,
            'high_risk_pension': True,
        })

        self.test_country = self.env.ref('base.co')

        self.test_state = self.env['res.country.state'].create(dict(
            name="State",
            code="ST",
            l10n_co_divipola="0001",
            country_id=self.test_country.id))

        self.town = self.env['res.country.town'].create(dict(
            name="town",
            code="TW",
            l10n_co_divipola="0011",
            state_id=self.test_state.id,
            country_id=self.test_country.id))

        self.contact = self.res_partner.create({
            'name': 'partner name',
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })

        self.employee = self.hr_employee.create({
            'name': "Test Payroll News",
            'names': "Test Payroll News",
            'surnames': "Test Payroll News",
            'known_as': "Test Payroll News",
            'document_type': '13',
            'contract_id': self.contract.id,
            'identification_id': "75395146",
            'address_home_id': self.contact.id,
            'high_risk_pension': True,
            'contributor_type': new_social_security.id,
            'contributor_subtype': new_social_security.id,
        })

        self.employee_id = self.hr_employee.create({
            'name': "Test Payroll News 2",
            'names': "Test Payroll News 2",
            'surnames': "Test Payroll News 2",
            'known_as': "Test Payroll News 2",
            'document_type': '13',
            'contract_id': self.contract_id.id,
            'identification_id': "75395149",
            'address_home_id': self.contact.id,
            'high_risk_pension': True,
            'contributor_type': new_social_security.id,
            'contributor_subtype': new_social_security.id,
        })

        self.payroll_structure = self.hr_payroll_structure.create({
            'name': "Structure Test",
            'sequence_id': self.ir_sequence_1.id,
            'type_id': self.structure_type.id,
        })

        self.salary_rule = self.hr_salary_rule.create({
            'name': "ITEM BASE",
            'l10n_type_rule': 'health',
            'code': "001",
            'sequence': 100,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1.0,
        })

        self.payslip = self.hr_payslip.create({
            'name': "Payroll Test",
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'struct_id': self.payroll_structure.id,
            'date_from': datetime.now()-timedelta(days=1),
            'date_to': datetime.now()+timedelta(days=30),
        })

        self.payslip_1 = self.hr_payslip.create({
            'name': "Payroll Test two",
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'struct_id': self.payroll_structure.id,
            'date_from': datetime.now()-timedelta(days=1),
            'date_to': datetime.now()+timedelta(days=30),
            'line_ids': [(0, 0, {
                'code': "TESTCODE",
                'salary_rule_id': self.salary_rule.id,
                'name': "SALARIO BÁSICO",
                'note': "sueldo / 30 X  los dias laborados",
                'quantity': 30.00,
            }), ]
        })

        self.payslip_2 = self.hr_payslip.create({
            'name': "Payroll Test two",
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'struct_id': self.payroll_structure.id,
            'date_from': datetime.now()-timedelta(days=1),
            'date_to': datetime.now()+timedelta(days=30),
            'line_ids': [(0, 0, {
                'code': "TESTCODE",
                'salary_rule_id': self.salary_rule.id,
                'name': "SALARIO BÁSICO",
                'note': "sueldo / 30 X  los dias laborados",
                'quantity': 30.00,
            }), ]
        })

        self.termination = self.ref(
            'hr_payroll_settlement.reason_dsjc_nor')

        self.settlement = self.env['settlement.history'].create({
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'date_payment': datetime.now(),
            'reason_for_termination': self.termination,
            'compensation': False,
            'payslip_id':  self.payslip_1.id
        })
    
    def test_generate_date(self):
        format = '%Y-%m-%d'
        Payslips._generate_date(self,format)

    def test_not_datedays_360(self):
        date1 = False
        date2 = datetime.now()+timedelta(days=15)
        logging.info(date2)
        Payslips.days_360(self,date1,date2)

    def test_datedays_360(self):
        date1 = datetime(2021, 8, 31)
        date2 = datetime(2021, 10, 31)
        logging.info(date2)
        Payslips.days_360(self,date1,date2)
    
    def test_datedays_2_360(self):
        date1 = datetime(2021, 8, 20)
        date2 = datetime(2021, 10, 20)
        logging.info(date2)
        Payslips.days_360(self,date1,date2)
    
    def test_get_contract_date_end(self):
        self.settlement.write({
            'date_payment': False
        })
        self.dict = self.payslip_1
        Payslips._get_contract_date_end(self)
    
    def test_get_contract_date_end_condition_date(self):
        self.settlement.write({
            'date_payment': datetime.now()+timedelta(days=15)
        })
        self.dict = self.payslip_1
        Payslips._get_contract_date_end(self)
    
    def test_get_all_worked_days_not_date_payment(self):
        self.settlement.write({
            'date_payment': False
        })
        self.dict = self.payslip_1
        date_start = datetime(2021, 8, 20)
        date_end = datetime(2021, 10, 20)
        Payslips._get_all_worked_days(self,date_start,date_end)

    
    def test_get_all_worked_days(self):
        self.dict = self.payslip_1
        date_start = datetime(2021, 8, 20)
        date_end = datetime(2021, 10, 20)
        Payslips._get_all_worked_days(self,date_start,date_end)
    
    def test_get_health_false_pension_value(self):
        self.dict = False
        Payslips._get_health_pension_value(self)
    
    def test_get_health_pension_value(self):
        self.dict = self.payslip_1
        Payslips._get_health_pension_value(self)

    def test_get_health_pension_fund_pension_value(self):
        self.salary_rule.write({
            'l10n_type_rule': 'pension_fund',
        })
        self.dict = self.payslip_2
        Payslips._get_health_pension_value(self)
    
    def test_get_health_pension_holydays_fund_pension_value(self):
        self.salary_rule.write({
            'l10n_type_rule': 'pension_fund',
        })
        self.payroll_structure.write({
            'name': 'Vacaciones',
        })
        self.dict = self.payslip_2
        Payslips._get_health_pension_value(self)
    
    def test_get_health_pension_holydays_2_fund_pension_value(self):
        self.salary_rule.write({
            'l10n_type_rule': 'health',
        })
        self.payroll_structure.write({
            'name': 'Vacaciones',
        })
        self.dict = self.payslip_2
        Payslips._get_health_pension_value(self)
    
    def test_truncate_decimals_strvalue(self):
        value = '123'
        decimals = 46
        Payslips.truncate_decimals(self, value, decimals)
    
    def test_truncate_decimals_value_negative(self):
        value = -4
        decimals = 46
        Payslips.truncate_decimals(self, value, decimals)
    
    def test_truncate_decimals_value_len_txt(self):
        value = -4
        decimals = 1
        Payslips.truncate_decimals(self, value, decimals)
    
    def test_round_value_dian_may_60(self):
        int_value = 0
        dec_value = 60
        Payslips.round_value_dian(self, int_value, dec_value)
    
    def test_round_value_dian_may_50(self):
        int_value = 0
        dec_value = 55
        Payslips.round_value_dian(self, int_value, dec_value)
    
    def test_round_value_dian_may_57(self):
        int_value = 0
        dec_value = 57
        Payslips.round_value_dian(self, int_value, dec_value)
    
    def test_round_value_dian(self):
        int_value = 3
        dec_value = 20
        Payslips.round_value_dian(self, int_value, dec_value)
    
    def test_datetime_now_user_tz(self):
        Payslips.datetime_now_user_tz(self)
    
    def test_update_tz(self):
        date_now = datetime.now()
        Payslips.update_tz(self,date_now)
    
    def test_get_date_end_employee(self):
        Payslips.get_date_end_employee(self)
    
    def test_get_date_end_employee(self):
        Payslips.get_date_end_employee(self)

    
    def test_get_recursive_contract_end(self):
        print('******************test_get_recursive_contract_end************************')
        contract_id = self.contract_id
        Payslips._get_recursive_contract_end(self, contract_id)
    
    def test_get_recursive_contract_end_2(self):
        print('*******************test_get_recursive_contract_end_2***********************')
        contract_id = self.contract_id
        Payslips._get_recursive_contract_end(self, contract_id)

    def test_get_recursive_contract_end_in_data_exclude(self):
        print('*******************test_get_recursive_contract_end_in_data_exclude***********************')
        self.contract.write({
            'state': 'cancel',
            'employee_id': self.employee_id.id
        })

        self.contract_id.write({
            'state': 'cancel',
            'employee_id': self.employee_id.id,
            'date_start': datetime.now()-timedelta(days=15),
        })

        self.contract2_id = self.hr_contract.create({
            'name': "Contract Test",
            'date_start': datetime.now()-timedelta(days=365),
            'date_end': datetime.now()+timedelta(days=365),
            'wage': 3150000,
            'structure_type_id': self.structure_type.id,
            'high_risk_pension': True,
            'state': 'cancel',
            'employee_id': self.employee_id.id,
        })
        print('***************contract2_id********************')
        print('***************************************self.contract2_id.date_start', self.contract2_id.date_start)
        print('***************************************self.contract2_id.date_end', self.contract2_id.date_end)
        print('***************************************self.contract2_id.state', self.contract2_id.state)
        print('***************************************self.contract2_id.employee_id', self.contract2_id.employee_id.id)
        print('***************************************self.contract2_id.id', self.contract2_id.id)
        contract_id = self.contract_id
        #exclude_ids = self.contract2_id.ids

        Payslips._get_recursive_contract_end(self, contract_id)

    """
    def test_get_date_start_employee(self):
        print('******************test_get_date_start_employee************************')
        Payslips.get_date_start_employee(self)
    """ 