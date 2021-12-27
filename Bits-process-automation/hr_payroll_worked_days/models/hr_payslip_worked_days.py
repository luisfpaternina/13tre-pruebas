from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    @api.onchange('number_of_days')
    def _onchange_value_worked_days(self):
        paid_amount = self.payslip_id._get_contract_wage()
        if self.payslip_id.contract_id.wage_type == 'monthly':
            if self.number_of_days > 31 or self.number_of_days < 0:
                raise ValidationError("The number of days is incorrect")
            date_from = fields.Datetime.from_string(
                self.payslip_id.date_from).date()
            date_to = fields.Datetime.from_string(
                self.payslip_id.date_to).date()
            _days = self.number_of_days
            _days = 30 if _days < 30 or _days == 31 else _days
            date_start = fields.Datetime.from_string(
                self.payslip_id.contract_id.date_start).date()
            if date_from <= date_start <= date_to:
                _days = _days - (date_start.day - 1)
            self.number_of_days = _days
