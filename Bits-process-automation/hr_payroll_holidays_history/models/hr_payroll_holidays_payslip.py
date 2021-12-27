from datetime import date, timedelta
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject


class MyHolidayPayslip(BrowsableObject):

    def _get_payroll_news(self, from_date, to_date):
        return self.env['hr.employee.payroll.news'].search(
            [
                ('employee_id', '=', self.employee_id),
                ('payroll_news_id.date_start', '>=', from_date),
                ('payroll_news_id.date_end', '<=', to_date),
                '|',
                ('payroll_news_id.stage_id.is_approved', '=', True),
                ('payroll_news_id.stage_id.is_won', '=', True)
            ])

    def compute_holidays(self, hour_extra_codes, comision_codes):
        contract = self.employee.contract_id
        date_from = date(
            self.enjoyment_start_date.year - 1,
            self.enjoyment_start_date.month,
            self.enjoyment_start_date.day) + timedelta(days=1)
        # self.enjoyment_start_date + timedelta(days=-360)
        novelties = self._get_payroll_news(
            date_from, self.enjoyment_start_date)
        # Horas extra
        hour_extra_ids = novelties.filtered(
            lambda line: line.payroll_news_id.salary_rule_code
            in hour_extra_codes)
        hour_extra_total = sum([line.total for line in hour_extra_ids])
        average_annual_overtime = (hour_extra_total * 30) / 360
        # Comisiones anuales
        annual_commissions_ids = novelties.filtered(
            lambda line: line.payroll_news_id.salary_rule_code
            in comision_codes)
        annual_commissions_total = sum(
            [line.total for line in annual_commissions_ids])
        overage_annual_commissions = (annual_commissions_total*30)/360

        return (contract.wage +
                average_annual_overtime +
                overage_annual_commissions)/30
