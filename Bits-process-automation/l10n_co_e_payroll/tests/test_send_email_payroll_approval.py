# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from datetime import datetime, timedelta, date


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
        self.send_email_payroll_approval = self.env['send.email.payroll.approval']

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
            'name': "ITEM BASE",
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
        })
        
        self.payslip = self.hr_payslip.create({
            'name': "Payroll Test",
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            'struct_id': self.payroll_structure.id,
            'date_from': datetime.now()-timedelta(days=1),
            'date_to': datetime.now()+timedelta(days=30),
        })

        self.wizard_email_send = self.send_email_payroll_approval.with_context(
            active_ids=[self.payslip_1.id, self.payslip_2.id]
        ).create(
            {
                'is_email': False,
                'is_print': True,
                'printed': False,
                'template_id': self.env.ref(
                    'hr_payroll_approval.approval_email_template'
                ).id,
                'partner_ids': [(self.contact.id)],
                'payslip_ids': [(6, 0, [self.payslip_1.id, self.payslip_2.id])]
            }
        )

    def test_send_and_print_action(self):
        self.wizard_email_send.send_and_print_action()
