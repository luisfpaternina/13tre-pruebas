# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError
from datetime import datetime, timedelta, date
import logging
_logger = logging.getLogger(__name__)


class ResConfigSettings(TransactionCase):

    def setUp(self):

        super(ResConfigSettings, self).setUp()
        self.res_config_settings = self.env['res.config.settings']
        self.hr_salary_rule = self.env['hr.salary.rule']
        self.hr_salary_rule_category = self.env['hr.salary.rule.category']
        self.hr_payroll_structure = self.env['hr.payroll.structure']
        self.hr_payroll_structure_type = self.env['hr.payroll.structure.type']
        self.res_company = self.env['res.company']
        # finish - Here I had 80 percent

    def test_check_there_is_transportation(self):
        self.res_company_one = self.res_company.create({
            'name': 'Test Company',
        })
        self.res_config_one = self.res_config_settings.create({
            'transportation_allowance': 0.0
        })
        self.res_config_two = self.res_config_settings.create({
            'transportation_allowance': 100000
        })
        self.res_config_three = self.res_config_settings.create({
            'transportation_allowance': False
        })

        self.res_config_four = self.res_config_settings.create({
            'transportation_allowance': -10000
        })
        self.env['ir.config_parameter'].sudo().set_param(
            'transportation_allowance', float(100))
        self.salary_rule_category = self.hr_salary_rule_category.create({
            'name': "Salary Category Test",
            'code': "SCT"
        })
        self.structure_type = self.hr_payroll_structure_type.create({
            'name': "Test Type",
            'wage_type': "monthly"
        })
        self.payroll_structure = self.hr_payroll_structure.create({
            'name': "Structure Test",
            'type_id': self.structure_type.id
        })
        self.salary_rule = self.hr_salary_rule.create({
            'name': "ITEM PARAFISCAL",
            'code': "001",
            'sequence': 100,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1.0,
            'l10n_type_rule': 'connectivity_rule',
        })
        self.salary_rule_two = self.hr_salary_rule.create({
            'name': "ITEM PARAFISCAL two",
            'code': "001",
            'sequence': 100,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1.0,
            'l10n_type_rule': 'advance_deductions',
        })
        # start - Here I had 80 percent
        self.salary_rule_three = self.hr_salary_rule.create({
            'name': "ITEM PARAFISCAL",
            'code': "001",
            'sequence': 100,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1.0,
            'l10n_type_rule': 'connectivity_rule',
        })
        self.res_config_one
        self.res_config_one._check_there_is_transportation()

    def test_check_there_is_transportation_two(self):
        self.res_company_one = self.res_company.create({
            'name': 'Test Company',
        })
        self.res_config_one = self.res_config_settings.create({
            'transportation_allowance': 0.0
        })
        self.res_config_two = self.res_config_settings.create({
            'transportation_allowance': 100000
        })
        self.res_config_three = self.res_config_settings.create({
            'transportation_allowance': False
        })

        self.res_config_four = self.res_config_settings.create({
            'transportation_allowance': -10000
        })
        self.env['ir.config_parameter'].sudo().set_param(
            'transportation_allowance', float(100))
        self.salary_rule_category = self.hr_salary_rule_category.create({
            'name': "Salary Category Test",
            'code': "SCT"
        })
        self.structure_type = self.hr_payroll_structure_type.create({
            'name': "Test Type",
            'wage_type': "monthly"
        })
        self.payroll_structure = self.hr_payroll_structure.create({
            'name': "Structure Test",
            'type_id': self.structure_type.id
        })
        self.salary_rule = self.hr_salary_rule.create({
            'name': "ITEM PARAFISCAL",
            'code': "001",
            'sequence': 100,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1.0,
            'l10n_type_rule': 'connectivity_rule',
        })
        self.salary_rule_two = self.hr_salary_rule.create({
            'name': "ITEM PARAFISCAL two",
            'code': "001",
            'sequence': 100,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1.0,
            'l10n_type_rule': 'advance_deductions',
        })
        # start - Here I had 80 percent
        self.salary_rule_three = self.hr_salary_rule.create({
            'name': "ITEM PARAFISCAL",
            'code': "001",
            'sequence': 100,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1.0,
            'l10n_type_rule': 'connectivity_rule',
        })
        self.res_config_two
        self.res_config_two._check_there_is_transportation()

    def test_check_there_is_transportation_three(self):
        self.res_company_one = self.res_company.create({
            'name': 'Test Company',
        })
        self.res_config_one = self.res_config_settings.create({
            'transportation_allowance': 0.0
        })
        self.res_config_two = self.res_config_settings.create({
            'transportation_allowance': 100000
        })
        self.res_config_three = self.res_config_settings.create({
            'transportation_allowance': False
        })

        self.res_config_four = self.res_config_settings.create({
            'transportation_allowance': -10000
        })
        self.env['ir.config_parameter'].sudo().set_param(
            'transportation_allowance', float(100))
        self.salary_rule_category = self.hr_salary_rule_category.create({
            'name': "Salary Category Test",
            'code': "SCT"
        })
        self.structure_type = self.hr_payroll_structure_type.create({
            'name': "Test Type",
            'wage_type': "monthly"
        })
        self.payroll_structure = self.hr_payroll_structure.create({
            'name': "Structure Test",
            'type_id': self.structure_type.id
        })
        self.salary_rule = self.hr_salary_rule.create({
            'name': "ITEM PARAFISCAL",
            'code': "001",
            'sequence': 100,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1.0,
            'l10n_type_rule': 'connectivity_rule',
        })
        self.salary_rule_two = self.hr_salary_rule.create({
            'name': "ITEM PARAFISCAL two",
            'code': "001",
            'sequence': 100,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1.0,
            'l10n_type_rule': 'advance_deductions',
        })
        # start - Here I had 80 percent
        self.salary_rule_three = self.hr_salary_rule.create({
            'name': "ITEM PARAFISCAL",
            'code': "001",
            'sequence': 100,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1.0,
            'l10n_type_rule': 'connectivity_rule',
        })
        self.res_config_three
        self.res_config_three._check_there_is_transportation()

    def test_check_there_is_transportation_four(self):
        self.res_company_one = self.res_company.create({
            'name': 'Test Company',
        })
        self.res_config_one = self.res_config_settings.create({
            'transportation_allowance': 0.0
        })
        self.res_config_two = self.res_config_settings.create({
            'transportation_allowance': 100000
        })
        self.res_config_three = self.res_config_settings.create({
            'transportation_allowance': False
        })

        self.res_config_four = self.res_config_settings.create({
            'transportation_allowance': -10000
        })
        self.env['ir.config_parameter'].sudo().set_param(
            'transportation_allowance', float(100))
        self.salary_rule_category = self.hr_salary_rule_category.create({
            'name': "Salary Category Test",
            'code': "SCT"
        })
        self.structure_type = self.hr_payroll_structure_type.create({
            'name': "Test Type",
            'wage_type': "monthly"
        })
        self.payroll_structure = self.hr_payroll_structure.create({
            'name': "Structure Test",
            'type_id': self.structure_type.id
        })
        self.salary_rule = self.hr_salary_rule.create({
            'name': "ITEM PARAFISCAL",
            'code': "001",
            'sequence': 100,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1.0,
            'l10n_type_rule': 'connectivity_rule',
        })
        self.salary_rule_two = self.hr_salary_rule.create({
            'name': "ITEM PARAFISCAL two",
            'code': "001",
            'sequence': 100,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1.0,
            'l10n_type_rule': 'advance_deductions',
        })
        # start - Here I had 80 percent
        self.salary_rule_three = self.hr_salary_rule.create({
            'name': "ITEM PARAFISCAL",
            'code': "001",
            'sequence': 100,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1.0,
            'l10n_type_rule': 'connectivity_rule',
        })
        self.res_config_four
        a = self.res_config_one._search_rule_object()
        self.res_config_four._check_there_is_transportation()

    def test_search_rule_object(self):
        self.res_company_one = self.res_company.create({
            'name': 'Test Company',
        })
        self.res_config_one = self.res_config_settings.create({
            'transportation_allowance': 0.0
        })
        self.res_config_two = self.res_config_settings.create({
            'transportation_allowance': 100000
        })
        self.res_config_three = self.res_config_settings.create({
            'transportation_allowance': False
        })

        self.res_config_four = self.res_config_settings.create({
            'transportation_allowance': -10000
        })
        self.env['ir.config_parameter'].sudo().set_param(
            'transportation_allowance', float(100))
        self.salary_rule_category = self.hr_salary_rule_category.create({
            'name': "Salary Category Test",
            'code': "SCT"
        })
        self.structure_type = self.hr_payroll_structure_type.create({
            'name': "Test Type",
            'wage_type': "monthly"
        })
        self.payroll_structure = self.hr_payroll_structure.create({
            'name': "Structure Test",
            'type_id': self.structure_type.id
        })
        a = self.res_config_one._search_rule_object()

    def test_check_there_is_transportation_five(self):
        self.res_company_one = self.res_company.create({
            'name': 'Test Company',
        })
        self.res_config_one = self.res_config_settings.create({
            'transportation_allowance': 0.0
        })
        self.res_config_two = self.res_config_settings.create({
            'transportation_allowance': 100000
        })
        self.res_config_three = self.res_config_settings.create({
            'transportation_allowance': False
        })

        self.res_config_four = self.res_config_settings.create({
            'transportation_allowance': -10000
        })
        self.env['ir.config_parameter'].sudo().set_param(
            'transportation_allowance', float(100))
        self.salary_rule_category = self.hr_salary_rule_category.create({
            'name': "Salary Category Test",
            'code': "SCT"
        })
        self.structure_type = self.hr_payroll_structure_type.create({
            'name': "Test Type",
            'wage_type': "monthly"
        })
        self.payroll_structure = self.hr_payroll_structure.create({
            'name': "Structure Test",
            'type_id': self.structure_type.id
        })
        self.salary_rule = self.hr_salary_rule.create({
            'name': "ITEM PARAFISCAL",
            'code': "001",
            'sequence': 100,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1.0,
            'l10n_type_rule': 'connectivity_rule',
        })
        self.salary_rule_two = self.hr_salary_rule.create({
            'name': "ITEM PARAFISCAL two",
            'code': "001",
            'sequence': 100,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1.0,
            'l10n_type_rule': 'advance_deductions',
        })
        # start - Here I had 80 percent
        self.salary_rule_three = self.hr_salary_rule.create({
            'name': "ITEM PARAFISCAL",
            'code': "001",
            'sequence': 100,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1.0,
            'l10n_type_rule': 'connectivity_rule',
        })
        self.res_config_four
        self.res_config_four._check_there_is_transportation()

    def test_compute_transportation_allowance_one(self):
        self.res_company_one = self.res_company.create({
            'name': 'Test Company',
        })
        self.res_config_one = self.res_config_settings.create({
            'transportation_allowance': 0.0
        })
        self.env['ir.config_parameter'].sudo().set_param(
            'transportation_allowance', float(100))
        self.salary_rule_category = self.hr_salary_rule_category.create({
            'name': "Salary Category Test",
            'code': "SCT"
        })
        self.structure_type = self.hr_payroll_structure_type.create({
            'name': "Test Type",
            'wage_type': "monthly"
        })
        self.payroll_structure = self.hr_payroll_structure.create({
            'name': "Structure Test",
            'type_id': self.structure_type.id
        })
        self.salary_rule = self.hr_salary_rule.create({
            'name': "ITEM PARAFISCAL",
            'code': "001",
            'sequence': 100,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1.0,
            'l10n_type_rule': 'connectivity_rule',
        })
        self.salary_rule
        self.res_config_one._compute_transportation_allowance()

    def test_compute_transportation_allowance_two(self):
        self.res_company_one = self.res_company.create({
            'name': 'Test Company',
        })
        self.res_config_one = self.res_config_settings.create({
            'transportation_allowance': 0.0
        })
        self.res_config_two = self.res_config_settings.create({
            'transportation_allowance': 100000
        })
        self.res_config_three = self.res_config_settings.create({
            'transportation_allowance': False
        })

        self.res_config_four = self.res_config_settings.create({
            'transportation_allowance': -10000
        })
        self.env['ir.config_parameter'].sudo().set_param(
            'transportation_allowance', float(100))
        self.salary_rule_category = self.hr_salary_rule_category.create({
            'name': "Salary Category Test",
            'code': "SCT"
        })
        self.structure_type = self.hr_payroll_structure_type.create({
            'name': "Test Type",
            'wage_type': "monthly"
        })
        self.payroll_structure = self.hr_payroll_structure.create({
            'name': "Structure Test",
            'type_id': self.structure_type.id
        })
        self.res_config_one._compute_transportation_allowance()
