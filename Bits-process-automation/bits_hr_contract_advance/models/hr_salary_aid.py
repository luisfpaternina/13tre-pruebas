from odoo import models, fields, api, _


class HrSalaryAid(models.Model):
    _name = 'hr.salary.aid'
    _description = _('Contains all salary aids')

    name = fields.Char('Name', size=45, required=True)
    description = fields.Char(string='Description', size=200, required=True)
    code = fields.Char(string='Code', size=5, required=True)

    _sql_constraints = [
        ('uk_hr_salary_aid',
         'unique(code)',
         'Your cannot have two salary aid with the same code')
    ]
