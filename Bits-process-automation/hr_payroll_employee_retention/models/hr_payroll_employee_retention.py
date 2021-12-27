from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta


class HrPayrollEmployeeRetention(models.Model):
    _name = 'hr.payroll.employee.retention'

    name = fields.Char(string="Description")
    employee_id = fields.Many2one(
        'hr.employee',
        required=True,
        string="Employee")
    identification_id = fields.Char(
        related='employee_id.identification_id',
        readonly=False,
        related_sudo=False)
    salary = fields.Float(digits=(12, 2))
    housing_incentive = fields.Float(digits=(12, 2), default="0")
    non_salary_bonus = fields.Float(digits=(12, 2))
    bonus = fields.Float(digits=(12, 2))
    vlnt_cntr_pension_fund_empl = fields.Float(
        digits=(12, 2),
        string="voluntary contribution to the employer's pension fund"
    )
    mandatory_pension_contributions = fields.Float(digits=(12, 2))
    mnd_cntr_pension_salidarity_fund = fields.Float(
        digits=(12, 2),
        string="Mandatory contributions to the Pension Solidarity Fund",
    )
    mnd_cntr_to_health = fields.Float(
        digits=(12, 2),
        string="Mandatory contributions to health"
    )
    vln_cntr_to_mnd_pension_fund = fields.Float(
        digits=(12, 2),
        string="Voluntary contributions to mandatory pension fund"
    )
    oth_inc_not_constituting_inc = fields.Float(
        digits=(12, 2),
        string="Other income not constituting income"
    )
    housing_interests = fields.Float(
        digits=(12, 2),
        string="Payment of housing interest \
            or Financial Cost Housing Leasing"
    )
    dependent_payments = fields.Float(
        digits=(12, 2),
        string="Payments for dependents"
    )
    prepaid_medicine_payments = fields.Float(
        digits=(12, 2),
        string="Payments for health prepaid medicine"
    )
    cntr_vlnt_pension_fund = fields.Float(
        digits=(12, 2),
        string="Contributions to voluntary pension fund"
    )
    cntr_afc_accounts = fields.Float(
        digits=(12, 2),
        string="Contributions to AFC accounts"
    )
    other_exempt_income = fields.Float(digits=(12, 2))
    exempt_labor_income = fields.Float(digits=(12, 2))

    labor_income = fields.Float(digits=(12, 2))
    total_non_constitutive_income = fields.Float(digits=(12, 2))
    subtotal1 = fields.Float(digits=(12, 2))
    total_deductions = fields.Float(digits=(12, 2))
    subtotal2 = fields.Float(digits=(12, 2))
    total_exempt_income = fields.Float(digits=(12, 2))
    subtotal3 = fields.Float(digits=(12, 2))
    subtotal4 = fields.Float(digits=(12, 2))
    ctrl_fgr_ddc_exempt_income = fields.Float(
        digits=(12, 2),
        string="Control figure 40% deductions and exempt income"
    )
    sum_deductions_exempt_income = fields.Float(digits=(12, 2))
    resutl_maximum_uvt = fields.Float(
        digits=(12, 2),
        string="Maximum Uvt allowed"
    )
    monthly_work_income = fields.Float(digits=(12, 2))
    income_taxed_uvt = fields.Float(digits=(12, 2))
    percent0 = fields.Float(digits=(12, 2), string="0%")
    percent19 = fields.Float(digits=(12, 2), string="19%")
    percent28 = fields.Float(digits=(12, 2), string="28%")
    percent33 = fields.Float(digits=(12, 2), string="33%")
    percent35 = fields.Float(digits=(12, 2), string="35%")
    percent37 = fields.Float(digits=(12, 2), string="37%")
    percent39 = fields.Float(digits=(12, 2), string="39%")
    amount = fields.Float(digits=(12, 2))
    payslip_id = fields.Many2one(
        'hr.payslip',
        string='Pay Slip',
        ondelete='cascade',
        index=True)
    payslip_name = fields.Char(
        string="Pay Slip Name",
        help=("This field will only"
              " be used when loading withholding records"))

    def _cron_execute_employee_retentions(self):
        date_now = fields.Datetime.today().date()
        datetime_min = fields.Datetime.today()
        datetime_max = datetime_min + relativedelta(
            hours=23, minutes=59, seconds=59)
        get_param = self.env['ir.config_parameter'].sudo().get_param
        str_date = get_param('str_date_truncate', default=False)
        str_date_exec = get_param('str_date_exec', default=False)

        if not str_date or not str_date_exec:
            return

        date_truncate = datetime.strptime(str_date, '%Y-%m-%d')
        date_execute = datetime.strptime(str_date_exec, '%Y-%m-%d').date()
        datetime_truncate = date_truncate + relativedelta(
            hours=23, minutes=59, seconds=59)

        if date_now != date_execute:
            return
        self.env['hr.payroll.employee.retention'].search([
            ('create_date', '<=', datetime_truncate)
        ]).unlink()

        set_param = self.env['ir.config_parameter'].sudo().set_param
        str_date_now = date_now.strftime('%d-%m-%Y')
        set_param('hr_payroll_employee_retention.str_date_prev', str_date_now)
