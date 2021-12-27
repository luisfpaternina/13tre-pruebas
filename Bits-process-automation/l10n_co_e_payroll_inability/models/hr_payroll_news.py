from odoo import fields, models, api, _


class HrPayrollNewsInherit(models.Model):
    _inherit = 'hr.payroll.news'

    inability_id = fields.Many2one(
        'hr.inability',
        'type of disability',
        domain="[('salary_rule_m2m_ids', '=', salary_rule_id)]"
        )

    check_inability_expense = fields.Boolean()
    inability_apply = fields.Boolean(
        related='salary_rule_id.inability_apply')

    @api.onchange('salary_rule_id')
    def _clear_domain_inability_id(self):
        self.inability_id = False
