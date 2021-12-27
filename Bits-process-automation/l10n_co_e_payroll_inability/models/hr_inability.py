from odoo import fields, models, _


class HrInability(models.Model):
    _name = 'hr.inability'
    _description = 'Hr Inability'

    name = fields.Char()
    code = fields.Integer()
    observation = fields.Text('Observation')
    salary_rule_m2m_ids = fields.Many2many('hr.salary.rule')
