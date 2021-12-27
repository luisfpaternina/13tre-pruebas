from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'
    basic_salary = fields.Float(string='basic salary')
