# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    l10n_type_rule = fields.Selection([
        ('connectivity_rule', 'DTR: Transporte'),
        ('advance_deductions', 'ANI: Advance of Deductions'),
        ('advance_accruals', 'ANT: Advance of accruals'),
        ('coi_commissions', 'COI: Commissions'),
        ('basic_salary', 'DBA: Basic salary'),
        ('enjoyment_rule', 'VAC: Enjoyment rule'),
        ('ded_voluntary_pension', 'DED: Voluntary pension'),
        ('ded_withholding_source', 'DED: Withholding at source'),
        ('ded_afc', 'DED: AFC'),
        ('ded_cooperative', 'DED: cooperative'),
        ('ded_tax_garnishment', 'DED: Tax garnishment'),
        ('ded_complementary_plans', 'DED: Complementary plans'),
        ('ded_education', 'DED: Education'),
        ('ded_refund', 'DED: Refund'),
        ('ded_debt', 'DED: Debt'),
        ('lib_payroll_credit', 'LIB: Payroll credit'),
        ('other_ded', 'ODE: Other deductions'),
        ('lic_leave_maternity', 'LIC: Maternity Leave'),
        ('lic_leave_paternity', 'LIC: Paternity Leave'),
        ('lic_leave_paid', 'LIC: Paid Leave'),
        ('lic_leave_unpaid', 'LIC: Unpaid Leave'),
        ('lic_leave_mourning', 'LIC: Mourning Leave'),
        ('health', 'SAL: Health'),
        ('pension_fund', 'FPE: Pension Fund'),
        ('soli_subs_fund', 'FSP: Solidarity and Subsistence Fund'),
        ('total_accrual', 'RES: Total Accrual'),
        ('total_payslip', 'RES: Total Payslip'),
        ('n_benefit_assistance', 'AUX: Auxilio no salarial'),
        ('benefit_assistance', 'AUX: Auxilio salarial'),
        ('s_bonus', 'BON: Bonificacion Salarial'),
        ('ns_bonus', 'BON: Bonificacion No salarial'),
        ('trans_connect_assistance', 'DTR: Sub Conectividad o Transporte'),
        ('public_sanction', 'SAN: Sanción Pública'),
        ('private_sanction', 'SAN: Sanción Privada'),
        ('inability', 'INC: Incapacidad'),
        ('hour_extra', 'HEX: Horas Extra'),
        ('compensated_holidays', 'VCO: VACACIONES EN DINERO'),
        ('payments_thirds', 'PAT: Payments to thirds'),
        ('accrued_sena_practice', 'DEV: Accrued sena pratice'),
        ('accrued_sena_elective', 'DEV: Accrued sena elective'),
        ('bonus_retirement', 'DEV: Bonus retirement'),
        ('compensation', 'DEV: Compensation'),
        ('reintegrate', 'DEV: Reintegrate'),
        ('legal_premium', 'PRI: Prima Legal'),
        ('extra_legal_premium', 'PRI: Prima Extralegal'),
        ('ces_annual_layoffs', 'CES: Cesantias Anuales'),
        ('ces_percentage_annual_layoffs',
            'CES: Intereses de Cesantias Anuales'),
        ('rule_rectificated_rpr', 'RPR: Rectificación de nomina individual'),
        ('rule_rectificated_nov', 'NOV: Rectificación de nomina individual'),
        ('rule_rectificated_not', 'NOT: Rectificación de nomina individual')],
        string='Category of the rule',
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
    )
    tech_provider_line_id = fields.Many2one(
        comodel_name='l10n_co.tech.provider.line',
        string="Tech Provider Line"
    )
    is_connectivity_rule = fields.Boolean(
        string='Do you want to calculate the transportation?',
        default=False,
    )
