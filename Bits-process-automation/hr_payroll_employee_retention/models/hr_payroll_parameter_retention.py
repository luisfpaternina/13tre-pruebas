from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class HrPayrollParameterRetention(models.Model):
    _name = 'hr.payroll.parameter.retention'

    @api.model
    def _get_dafault_country(self):
        country = self.env['res.country'].search(
            [('code', '=', 'CO')], limit=1)
        return country.id

    @api.model
    def _get_dafault_currency(self):
        return self.env.company.currency_id.id

    name = fields.Char(string="Name")
    year = fields.Integer(string='Year', size=4, required=True, index=True)
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency', default=_get_dafault_currency)
    minimum_wage = fields.Monetary(
        string="Minimum Wage", currency_field='currency_id')
    transportation_allowance = fields.Monetary(
        string="Transportation Allowance")
    minimum_integral = fields.Monetary(string="Minimum Integral")
    uvt = fields.Monetary(string="UVT")
    exempt_cap = fields.Monetary(string="Exempt Cap")
    maximum_food_salary = fields.Monetary(string="Maximum Food Salary")
    housing_cap = fields.Monetary(string="Housing Cap")
    solidarity_cap = fields.Integer(string="Solidarity Cap")
    top_income_previous_year = fields.Monetary(
        string="Top Income Previous Year")
    exempt_income_cap = fields.Monetary(string="Exempt Income Cap")
    cap_health = fields.Monetary(string="Cap Health")
    dependent_certificate_cap = fields.Monetary(
        string="Dependent Certificate Cap")
    social_security_cap = fields.Integer(string="Social Security Cap")
    country_parameter = fields.Many2one('res.country', string="Country",
                                        default=_get_dafault_country)
    check_figure = fields.Integer(string="Check Figure")
    uvt_allowed = fields.Integer(string="UVT Allowed")

    _sql_constraints = [
        ('year_params_uniq', 'unique(year)',
         'There is already a parameter of law registered for this year'),
    ]
