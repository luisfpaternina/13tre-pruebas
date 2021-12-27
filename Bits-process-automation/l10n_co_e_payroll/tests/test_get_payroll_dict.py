# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from datetime import datetime, timedelta, date
import logging
from odoo.addons.l10n_co_e_payroll.models.browsable_object\
    import Payslips

from odoo.addons.bits_api_connect.models.adapters.builder_file_adapter\
    import BuilderToFile

import logging
_logger = logging.getLogger(__name__)


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
        self.ir_sequence = self.env['ir.sequence']
        self.hr_payslip_line = ['hr.payslip.line']
        self.payment_method_class = self.env['payment.method']
        self.payment_way_class = self.env['payment.way']
        self.hr_payroll_news_stage = self.env['hr.payroll.news.stage']
        self.hr_payroll_new = self.env['hr.payroll.news']
        self.hr_payroll_holidays_history = self.env['hr.payroll.holidays.history']
        self.hr_payroll_holiday_lapse = self.env['hr.payroll.holiday.lapse']

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

        self.payroll_structure = self.hr_payroll_structure.create({
            'name': "Structure Test",
            'sequence_id': self.ir_sequence_1.id,
            'type_id': self.structure_type.id,
        })

        self.salary_rule = self.hr_salary_rule.create({
            'name': "Clean Salary Rule",
            'code': "CLN",
            'sequence': 10,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1,
        })

        self.salary_rule_afc = self.hr_salary_rule.create({
            'name': "ITEM BASE",
            'code': "001",
            'sequence': 100,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1,
            'l10n_type_rule': 'ded_afc',
            'tech_provider_line_id': self.env.ref('l10n_co_tech_provider_payroll.l10n_co_tech_provider_payroll_line_headboard_38').id
        })

        parent_act_field_indicator = self.env.ref('l10n_co_tech_provider_payroll.l10n_co_tech_provider_payroll_line_headboard_37')
        parent_act_field_indicator.act_field_id = self.env.ref('l10n_co_payroll_act_fields.payroll_act_fields_148').id

        self.salary_rule_parent_act_field = self.hr_salary_rule.create({
            'name': "TESTACTF",
            'code': "TESTACTF",
            'sequence': 150,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 2500,
            'quantity': 1,
            'l10n_type_rule': 'ded_refund',
            'tech_provider_line_id': parent_act_field_indicator.id
        })

        act_field_false_indicator = self.env.ref('l10n_co_tech_provider.l10n_co_tech_provider_payroll_line_field_144')
        act_field_false_act_field = self.env.ref('l10n_co_payroll_act_fields.payroll_act_fields_144')
        act_field_false_act_field.condition_select = 'python'
        act_field_false_act_field.validate_condition_select = 'payslip == False'
        act_field_false_indicator.act_field_id = act_field_false_act_field.id

        act_child_false_condition = self.env.ref('l10n_co_payroll_act_fields.payroll_act_fields_145')
        act_child_false_condition.condition_select = 'python'
        act_child_false_condition.validate_condition_select = 'result = False'

        parent_parent_indicator = self.env.ref('l10n_co_tech_provider_payroll.l10n_co_tech_provider_payroll_line_headboard_33')
        parent_parent_act_field = self.env.ref('l10n_co_payroll_act_fields.payroll_act_fields_133')
        parent_parent_act_field.condition_python = "result = [x for x in payslip_line.salary_rule_id.tech_provider_line_id.children_ids]"
        parent_parent_indicator.act_field_id = parent_parent_act_field.id

        self.salary_rule_act_field_false = self.hr_salary_rule.create({
            'name': "ACTFFALSE",
            'code': "ACTFFALSE",
            'sequence': 150,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 2500,
            'quantity': 1,
            'tech_provider_line_id': act_field_false_indicator.id
        })

        lic_indicator = self.env.ref('l10n_co_tech_provider_payroll.l10n_co_tech_provider_payroll_line_headboard_18')
        lic_indicator.cardinality = '0_1'

        self.salary_rule_lic = self.hr_salary_rule.create({
            'name': 'LIC',
            'code': 'LIC',
            'sequence': 200,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'affect_payslip': False,
            'constitutive_calculate': True,
            'quantity': 1.0,
            'amount_select': "percentage",
            'amount_percentage': 100.0,
            'amount_percentage_base': "contract.wage/30",
            'l10n_type_rule': 'lic_leave_maternity',
            'tech_provider_line_id': lic_indicator.id,
        })

        pat_indicator = self.env.ref('l10n_co_tech_provider_payroll.l10n_co_tech_provider_payroll_line_headboard_35')
        pat_indicator.cardinality = '1_1'
        act_field_pat = self.env.ref('l10n_co_tech_provider.l10n_co_tech_provider_payroll_line_field_137')
        act_field_pat.cardinality = '1_1'
        act_field_pat_child = self.env.ref('l10n_co_tech_provider.l10n_co_tech_provider_payroll_line_field_138')
        act_field_pat_child.parent_id = act_field_pat.id

        dev_indicator = self.env.ref('l10n_co_tech_provider_payroll.l10n_co_tech_provider_payroll_line_headboard_28')
        dev_indicator.cardinality = '1_1'
        act_field_dev = self.env.ref('l10n_co_tech_provider.l10n_co_tech_provider_payroll_line_field_117')
        act_field_dev.cardinality = '1_1'
        act_field_dev.act_field_id.condition_python = "result = [x.salary_rule_id.tech_provider_line_id for x in payslip.line_ids]"
        act_field_dev_child = self.env.ref('l10n_co_tech_provider.l10n_co_tech_provider_payroll_line_field_118')
        act_field_dev_child.parent_id = act_field_dev.id

        self.salary_rule_pat = self.hr_salary_rule.create({
            'name': 'PAT',
            'code': 'PAT',
            'sequence': 250,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'affect_payslip': False,
            'constitutive_calculate': True,
            'quantity': 1.0,
            'amount_select': "percentage",
            'amount_percentage': 100.0,
            'amount_percentage_base': "contract.wage/30",
            'tech_provider_line_id': act_field_pat.id,
        })

        self.salary_rule_vac = self.hr_salary_rule.create({
            'name': 'VAC',
            'code': 'VAC',
            'sequence': 300,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'affect_payslip': False,
            'constitutive_calculate': True,
            'quantity': 1.0,
            'amount_select': "percentage",
            'amount_percentage': 100.0,
            'amount_percentage_base': "holiday.compute_holidays(hour_extra_codes=['60','65','70','75'],comision_codes=['321'])",
            'l10n_type_rule': 'enjoyment_rule',
            'tech_provider_line_id': self.env.ref(
                'l10n_co_tech_provider_payroll.l10n_co_tech_provider_payroll_line_headboard_13'
            ).id
        })

        self.salary_rule_child_parent = self.hr_salary_rule.create({
            'name': "CHILDP",
            'code': "CHILDP",
            'sequence': 400,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 2500,
            'quantity': 1,
            'tech_provider_line_id': parent_parent_indicator.id
        })

        self.payrol_news_stage = self.hr_payroll_news_stage.create({
            'name': "Stage Test"
        })

        self.payroll_new = self.hr_payroll_new.create({
            'name': "Test Novelty",
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule_lic.id,
            'stage_id': self.payrol_news_stage.id,
            'employee_payroll_news_ids': [
                [
                    0,
                    0,
                    {
                        'quantity': 1,
                        'employee_id': self.employee.id,
                        'amount': 5
                    }
                ]
            ],
            'datetime_end': datetime.now(),
            'datetime_start': datetime.now()+timedelta(days=5),
        })

        self.payroll_new_lic_2 = self.hr_payroll_new.create({
            'name': "Test Novelty",
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule_lic.id,
            'stage_id': self.payrol_news_stage.id,
            'employee_payroll_news_ids': [
                [
                    0,
                    0,
                    {
                        'quantity': 1,
                        'employee_id': self.employee.id,
                        'amount': 5
                    }
                ]
            ],
            'datetime_end': datetime.now(),
            'datetime_start': datetime.now()+timedelta(days=5),
        })

        self.holiday_lapse_vac = self.hr_payroll_holiday_lapse.create({
            'employee_id': self.employee.id,
            'begin_date': datetime.now()-timedelta(days=15),
            'end_date': datetime.now()+timedelta(days=15),
            'number_holiday_days': 30,
            'type_vacation': 'normal',
            'state': '2',
        })

        holiday_start_date = datetime.now()-timedelta(days=3)
        holiday_end_date = datetime.now()+timedelta(days=3)

        self.holiday_history_vac = self.hr_payroll_holidays_history.create({
            'name': "Test Vacations",
            'employee': self.employee.id,
            'holiday_lapse': self.holiday_lapse_vac.id,
            'enjoyment_start_date': holiday_start_date.strftime('%Y-%m-%d'),
            'enjoyment_end_date': holiday_end_date.strftime('%Y-%m-%d'),
            'enjoyment_days': 6,
            'compensated_days': 0,
            'payment_date': datetime.now(),
            'liquidated_period': 'month',
        })

        self.payroll_new_vac = self.hr_payroll_new.create({
            'name': "Test Vacations",
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule_vac.id,
            'stage_id': self.payrol_news_stage.id,
            'employee_payroll_news_ids': [
                (
                    0,
                    0,
                    {
                        'quantity': 1,
                        'employee_id': self.employee.id,
                        'amount': 5
                    }
                ),
            ],
            'holiday_history_id': self.holiday_history_vac.id,
            'datetime_end': datetime.now(),
            'datetime_start': datetime.now()+timedelta(days=5),
        })

        self.payroll_new_vac_2 = self.hr_payroll_new.create({
            'name': "Test Vacations 2",
            'payroll_structure_id': self.payroll_structure.id,
            'salary_rule_id': self.salary_rule_vac.id,
            'stage_id': self.payrol_news_stage.id,
            'employee_payroll_news_ids': [
                (
                    0,
                    0,
                    {
                        'quantity': 1,
                        'employee_id': self.employee.id,
                        'amount': 5
                    }
                ),
            ],
            'holiday_history_id': self.holiday_history_vac.id,
            'datetime_end': datetime.now(),
            'datetime_start': datetime.now()+timedelta(days=5),
        })

        self.payment_method = self.payment_method_class.create({
            'name': 'Payroll MC Test',
            'code': 'PMCTEST',
        })

        self.payment_way = self.payment_way_class.create({
            'name': 'Payroll WC Test',
            'code': 'PWCTEST',
        })

        self.payslip = self.hr_payslip.create({
            'name': "Payroll Test",
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'struct_id': self.payroll_structure.id,
            'date_from': datetime.now()-timedelta(days=1),
            'date_to': datetime.now()+timedelta(days=30),
            'line_ids': [(0, 0, {
                'code': "TESTCODE",
                'salary_rule_id': self.salary_rule_afc.id,
                'name': "SALARIO BÁSICO",
                'note': "sueldo / 30 X  los dias laborados",
                'quantity': 3000,
                'rate': 100,
                'amount': 3000,
            }),
            (0, 0, {
                'code': "LIC",
                'salary_rule_id': self.salary_rule_lic.id,
                'name': "LIC",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
                'payroll_news_id': [(4, self.payroll_new.id)]
            }),
            (0, 0, {
                'code': "LIC_2",
                'salary_rule_id': self.salary_rule_lic.id,
                'name': "LIC_2",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
                'payroll_news_id': [(4, self.payroll_new_lic_2.id)]
            }),
            (0, 0, {
                'code': "VAC",
                'salary_rule_id': self.salary_rule_vac.id,
                'name': "VAC",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
                'payroll_news_id': [(4, self.payroll_new_vac.id)]
            }),
            (0, 0, {
                'code': "VAC2",
                'salary_rule_id': self.salary_rule_vac.id,
                'name': "VAC2",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
                'payroll_news_id': [(4, self.payroll_new_vac.id)]
            }),
            (0, 0, {
                'code': "VAC2",
                'salary_rule_id': self.salary_rule_vac.id,
                'name': "VAC2",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
                'payroll_news_id': [(4, self.payroll_new_vac_2.id)]
            }),
            (0, 0, {
                'code': "ACTF",
                'salary_rule_id': self.salary_rule_parent_act_field.id,
                'name': "ACTF",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
            }),
            (0, 0, {
                'code': "CLN",
                'salary_rule_id': self.salary_rule.id,
                'name': "CLN",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
            }),
            (0, 0, {
                'code': "ACTFFALSE",
                'salary_rule_id': self.salary_rule_act_field_false.id,
                'name': "ACTFFALSE",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
            }),
            (0, 0, {
                'code': "CHILDP",
                'salary_rule_id': self.salary_rule_child_parent.id,
                'name': "CHILDP",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
            }),
            (0, 0, {
                'code': "PAT",
                'salary_rule_id': self.salary_rule_pat.id,
                'name': "PAT",
                'note': "sueldo / 30",
                'quantity': 5,
                'rate': 100,
                'amount': 3000,
            }), ],
            'payment_method_id': self.payment_method.id,
            'payment_way_id': self.payment_way.id,
        })
        
        child_1 = self.env.ref('l10n_co_tech_provider.l10n_co_tech_provider_payroll_line_field_004')
        child_1.cardinality = '1_1'
                
        child_2 = self.env.ref('l10n_co_tech_provider.l10n_co_tech_provider_payroll_line_field_005')
        child_2.parent_id = child_1.id

        emp_indicator = self.env.ref('l10n_co_tech_provider_payroll.l10n_co_tech_provider_payroll_line_headboard_02')
        emp_indicator.act_field_id = self.env.ref('l10n_co_payroll_act_fields.payroll_act_fields_012').id

    def test_action_generate_file_multi_line(self):
        
        config = self.env['res.config.settings'].create({})
        config.active_tech_provider = True
        config.provider_payroll_id = self.tech_provider_1.id
        config.execute()

        self.payslip.company_id.vat = '123456789'
        self.payslip.company_id.partner_id.write({
            'country_id': self.test_country.id,
            'town_id': self.town.id,
            'state_id': self.test_state.id
        })
        self.employee.address_home_id.write({
            'country_id': self.env.ref('base.co')})
        self.payslip.action_generate_file()