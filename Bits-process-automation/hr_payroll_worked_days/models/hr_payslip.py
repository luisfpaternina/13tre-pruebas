import calendar
from odoo import api, fields, models, _
from datetime import datetime, date


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def change_number_days_hours(self, Worked_days_list, contract_id):
        date_from = datetime(self.date_from.year,
                             self.date_from.month, self.date_from.day, 0, 0, 1)
        date_to = datetime(self.date_to.year, self.date_to.month,
                           self.date_to.day, 23, 59, 59)
        month_days = self.date_to.day
        leave_days = self.employee_id._get_leave_days_data(date_from, date_to)
        month_days = 30 if month_days < 30 or month_days == 31 else month_days
        date_start = fields.Datetime.from_string(
            contract_id.date_start).date()
        if date_from.date() <= date_start <= date_to.date():
            month_days = month_days - (date_start.day - 1)
        hour_days = (
            (contract_id.resource_calendar_id.full_time_required_hours*4) -
            leave_days.get('hours', 0))

        paid_amount = self._get_contract_wage()
        res = []
        for work_days in Worked_days_list:
            Work_entry_id = work_days.get('work_entry_type_id', False)
            work_entry = self.env['hr.work.entry.type'].browse(Work_entry_id)
            if work_entry.code != 'WORK100':
                continue
            work_days['number_of_days'] = month_days
            work_days['number_of_hours'] = hour_days
            work_days['amount'] = paid_amount
            res.append(work_days.copy())
        return res

    def _get_worked_day_lines(self):
        contract_id = self.contract_id
        Worked_days_list = super(HrPayslip, self)._get_worked_day_lines()
        if contract_id.wage_type == 'monthly':
            return self.change_number_days_hours(Worked_days_list, contract_id)
        return Worked_days_list
