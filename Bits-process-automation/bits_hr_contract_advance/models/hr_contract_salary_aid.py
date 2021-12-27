from odoo import models, fields, api, _


class HrContractSalaryAid(models.Model):
    _name = 'hr.contract.salary.aid'
    _description = _('represents intermediate table'
                     ', an contract can have many salary aid')

    value = fields.Float(string='Value', default=0, required=True)
    contract_id = fields.Many2one(
        'hr.contract', string='Contract', required=True)
    salary_aid_id = fields.Many2one(
        'hr.salary.aid', string='Salary aid', required=True)

    _sql_constraints = [
        ('uk_hr_contract_salary_aid',
         'unique(contract_id, salary_aid_id)',
         'You cannot have the same salary aid assigned more than once')
    ]
