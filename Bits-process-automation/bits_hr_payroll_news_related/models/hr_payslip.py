from odoo import api, fields, models, _
from odoo.tools import float_round


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def search_payroll_news(self):
        payroll_news_ids = self.env['hr.employee.payroll.news'].search(
            [('employee_id', '=', self.employee_id.id),
             ('payroll_news_id.date_start', '>=', self.date_from),
             # ('payroll_news_id.date_end', '<=', self.date_to),
             ('payroll_news_id.stage_id.is_approved', '=', True)])
        return payroll_news_ids

    def get_vals_lines_payslip(self, salary_rule, payroll_news):
        line_payslip = {
            'sequence': salary_rule.sequence,
            'code': salary_rule.code,
            'name': salary_rule.name,
            'salary_rule_id': salary_rule.id,
            'amount': payroll_news.amount,
            'quantity': payroll_news.quantity,
            'slip_id': self.id,
            'payroll_news_id': [payroll_news.payroll_news_id.id],
            'rate': salary_rule.amount_percentage or 100,
            'total': payroll_news.total
        }
        return line_payslip

    def get_news_by_rule(self, payroll_news_ids):
        payroll_news_dict = {}
        for payroll_news in payroll_news_ids:
            salary_rule = payroll_news.payroll_news_id.salary_rule_id
            dict_key = payroll_news.payroll_news_id.salary_rule_id.code
            if not payroll_news_dict.get(dict_key, False):
                payroll_news_dict[dict_key] = self.get_vals_lines_payslip(
                    salary_rule, payroll_news)
                continue
            dict_rule = payroll_news_dict.get(dict_key, False)
            dict_rule['quantity'] = dict_rule['quantity']+payroll_news.quantity
            dict_rule['payroll_news_id'] = (
                dict_rule['payroll_news_id']+[
                    payroll_news.payroll_news_id.id])
            dict_rule['total'] += payroll_news.total
        return payroll_news_dict

    def get_list_payroll_news(self):
        payroll_news_ids = self.search_payroll_news()
        payroll_news_dict = self.get_news_by_rule(payroll_news_ids)
        list_payroll_new = []
        for key, value in payroll_news_dict.items():
            value['amount'] = value['total']/value['quantity']
            value['total'] = (
                value['total']*-1
                if value.get('rate', 0.0) < 0.0 else value.get('total', 0.0))
            list_payroll_new.append(value)
        return list_payroll_new

    def add_salary_rule(self):
        result = super(HrPayslip, self).add_salary_rule()
        result += self.get_list_payroll_news()
        return result

    def _state_liquidity_news(self):
        stage_won_id = self.env['hr.payroll.news.stage'].search([
            ('is_won', '=', True)])
        payslip_news_ids = []
        for line in self.line_ids:
            payslip_news_ids += line.payroll_news_id.ids
        payslip_news_ids = (
            self.env['hr.payroll.news'].browse(
                payslip_news_ids) if payslip_news_ids else [])
        for payslip_news_id in payslip_news_ids:
            payslip_news_id.write({
                "stage_id": stage_won_id[0].id
            })

    def approve_payroll(self):
        result = super(HrPayslip, self).approve_payroll()
        self._state_liquidity_news()
        return result
