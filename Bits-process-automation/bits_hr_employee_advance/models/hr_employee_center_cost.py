from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrEmployeeCenterCost(models.Model):
    _name = 'hr.employee.center.cost'
    _description = (
        'represents intermediate table, an employee can have many center.cost'
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required="True"
    )
    name = fields.Char(string='Name')
    percentage = fields.Float('Percentage', required="True")
    account_analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Account analytic',
        required="True"
    )

    _sql_constraints = [
        (
            'uk_employee_and_center',
            'unique(employee_id, account_analytic_id)',
            'An employee cannot have the same cost center twice'
        )]
