from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _


class HrContractHistory(models.Model):
    _name = 'hr.contract.history'

    _order = "id"

    contract_id = fields.Many2one(
        'hr.contract', string='Contract', required=True)
    date = fields.Date(
        required=True,
        default=datetime.now())
    description = fields.Text()
    last_salary = fields.Float(
        default=0,
        required=True)
    amount = fields.Float(
        default=0,
        required=True)
    _type = fields.Selection([
        ('wage', 'Wage'),
    ], required=True, default='wage')
    adjusment_date = fields.Date(
        'Adjusment date',
        required=True)

    @api.constrains('contract_id')
    def _adjusment_date_val(self):
        for history in self:
            payrolls = self.env['hr.payslip'].search([
                ('date_from', '<=', history.adjusment_date),
                ('date_to', '>=', history.adjusment_date),
                ('employee_id', '=', history.contract_id.employee_id.id)
            ])

            history.adjusment_date = (history.adjusment_date
                                      if not payrolls
                                      else history.adjusment_date
                                      + relativedelta(day=1, months=+1))
