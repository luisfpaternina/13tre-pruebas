from odoo import api, fields, models, _
from odoo.tools import float_round


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    payroll_news_id = fields.Many2many('hr.payroll.news', invisible=1)

    @api.depends('quantity', 'amount', 'rate')
    def _compute_total(self):

        apply_lines = self.filtered(lambda line: line.salary_rule_id.apply_in == 'total')
        codes = []
        for line in apply_lines:
            codes += line.salary_rule_id.apply_other_rules.split(',')

        for line in self:
            if len(line.payroll_news_id) > 1 \
                or line.code in codes:
                continue
            line.total = float(line.quantity) * line.amount * line.rate / 100
        super(HrPayslipLine, self)._compute_total()
