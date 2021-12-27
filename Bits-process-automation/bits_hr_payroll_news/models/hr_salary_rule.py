# Part of Bits. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval


class HrPayrollStructureType(models.Model):
    _inherit = 'hr.payroll.structure.type'

    is_novelty = fields.Boolean(default=False)


class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    is_novelty = fields.Boolean(
        related='type_id.is_novelty',
        invisible=1)

    date_range_apply = fields.Boolean(
        default=False,
        help="It allows to add range of start date and end date \
        for the payroll mews.")

    @api.model
    def _get_default_rule_ids(self):
        res = super(HrPayrollStructure, self)._get_default_rule_ids()
        translations = dict(NET='Neto a Pagar')
        # Se agrega el campo appears_on_payslip
        appears_on_payslip = dict(NET=False, GROSS=False)

        for line in [x for x in res if x[2]['code'] in translations]:
            line[2]['name'] = translations.get(line[2]['code'])

        for line in [x for x in res if x[2]['code'] in appears_on_payslip]:
            line[2]['appears_on_payslip'] = (
               appears_on_payslip.get(line[2]['code']))

        return res

    rule_ids = fields.One2many(
        'hr.salary.rule', 'struct_id',
        string='Salary Rules', default=_get_default_rule_ids)


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    constitutive = fields.Selection([
        ('none', 'Not apply'),
        ('non_const', 'Not Constitutive'),
        ('is_const', 'Constitutive'),
    ], default='is_const', help="Allows adding the rule to the \
        calculation of the constitutive concepts.")

    constitutive_calculate = fields.Boolean(
        default=False,
        help="Calculate the rule with the sum of all the constitutive \
        concepts?")

    constitutive_percentage = fields.Float(
        string="Percentage constitutive (%)",
        default=100,
        digits='Payroll Rate')

    non_constitutive_percentage = fields.Float(
        string="Percentage non-constitutive (%)",
        default=100,
        digits='Payroll Rate')

    non_const_percentage_up = fields.Float(
        string="Percentage non-constitutive up (%)",
        default=0,
        digits='Payroll Rate')

    non_constitutive_calculate = fields.Boolean(
        default=False,
        help="Calculate the rule with the sum of all the non-constitutive \
        concepts?")

    affect_payslip = fields.Boolean(default=True)

    # Se agrega campo para especificar si la regla
    # aparecera en el desprendible de vacaciones
    appears_on_holidays = fields.Boolean(
        string="Appears on Holidays",
        default=False
    )

    affect_worked_days = fields.Boolean(default=False)
    affect_percentage_days = fields.Float(default=1.0)

    benefit_calculate = fields.Selection([
        ('none', 'All'),
        ('rem_work_days', 'Remunerate Work days'),
        ('non_rem_work_days', 'No Remunerate Work days')
    ], default='none',
        help="Lets make the deduction for the days included in the rule.")

    fields.Boolean(default=False)

    not_remunerate = fields.Boolean(default=False)

    date_range_apply = fields.Boolean(
        related='struct_id.date_range_apply',
        invisible=1)

    condition_holiday = fields.Selection([
        ('none', 'All'),
        ('work_days', 'Work days'),
        ('non_work_days', 'Non-working days')
    ], string="Calculate days based on", default='none',
        help="If it is checked, the days taken to calculate the holidays \
       are taken from non-working days.", required=True)

    apply_only_basic_salary = fields.Boolean(default=False)
    apply_only_const = fields.Boolean(default=False)
    apply_other_rules = fields.Char()
    apply_in = fields.Selection([
        ('amount', 'Amount'),
        ('total', 'Total')
    ])

    amount_fix = fields.Float(digits='Amount fix')

    exclude_other_rules = fields.Char(string="Exclude in Other Rules")
    exclude_in = fields.Selection(
        [
            ('amount', 'Amount'),
            ('total', 'Total')
        ],
        string="Exclude In"
    )

    percentaje_fsd = fields.Float(digits='Percentaje FDS')
    rule_constitutive = fields.Char('Rules Constitutive')
    rule_non_constitutive = fields.Char('Rules Constitutive')
    include_holidays_fds = fields.Char('Rules Holidays')

    affect_const_non_const = fields.Boolean(
        "Affect constitutive/non constitutive values"
    )

    @api.model
    def create(self, vals):
        code = vals.get('code', '')
        if code == 'BASIC':
            vals['constitutive'] = 'is_const'
        return super(HrSalaryRule, self).create(vals)
