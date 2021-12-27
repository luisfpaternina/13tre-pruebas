# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare, float_is_zero


class HrPayrollAccountPartner(models.Model):
    _inherit = ['hr.payslip']

    def _get_validate_sign_value(self, value):
        result = 1 if value > 0.0 else -1
        return result

    def _validate_value_lines(self, debit_account, credit_account,
                              paylip_line):
        debit_value = 0.0
        credit_value = 0.0
        context = self._context
        amount = (context.get('total_by_news', False)
                  if context.get('total_by_news', False)
                  else paylip_line.total)
        if debit_account:
            debit_value = (amount if amount > 0.0
                           else 0.0)
            credit_value = (-amount if amount < 0.0
                            else 0.0)
        if credit_account:
            debit_value = (-amount if amount < 0.0
                           else 0.0)
            credit_value = (amount if amount > 0.0
                            else 0.0)
        if credit_account and amount < 0.0:
            credit_value = (-amount if amount < 0.0
                            else 0.0)
            debit_value = 0.0
        return debit_value, credit_value

    def get_employee_news(self, slip, payroll_news_id):
        employee_payroll_news = self.env[
            'hr.employee.payroll.news'].search([
                ('employee_id', '=', slip.employee_id.id),
                ('payroll_news_id', '=', payroll_news_id.id)])
        return employee_payroll_news

    def generate_line_parafiscal(self, salary_rule, paylip_line, move,
                                 slip, partner, date, social_security_ids,
                                 employee_center_costs):
        line_ids = []
        if paylip_line.payroll_news_id:
            for payroll_news_id in paylip_line.payroll_news_id:
                employee_payroll_news = self.get_employee_news(
                    slip, payroll_news_id)
                context = dict(self._context,
                               total_by_news=(
                                   employee_payroll_news.total *
                                   self._get_validate_sign_value(
                                       paylip_line.rate)))
                line_ids += super(HrPayrollAccountPartner,
                                  self.with_context(context)
                                  ).generate_line_parafiscal(
                    salary_rule, paylip_line, move, slip, partner,
                    date, social_security_ids, employee_center_costs)
            return line_ids
        return super(HrPayrollAccountPartner, self).generate_line_parafiscal(
            salary_rule, paylip_line, move, slip, partner,
            date, social_security_ids, employee_center_costs)

    def generate_line_center_cost(self, employee_center_costs, salary_rule,
                                  paylip_line, date, move_id, partner, move,
                                  slip):
        line_ids = []
        if paylip_line.payroll_news_id:
            for payroll_news_id in paylip_line.payroll_news_id:
                employee_payroll_news = self.get_employee_news(
                    slip, payroll_news_id)
                context = dict(self._context,
                               total_by_news=(
                                   employee_payroll_news.total *
                                   self._get_validate_sign_value(
                                       paylip_line.rate)))
                line_ids += super(HrPayrollAccountPartner,
                                  self.with_context(context)
                                  ).generate_line_center_cost(
                                      employee_center_costs, salary_rule,
                                      paylip_line, date, move_id, partner,
                                      move, slip)
            return line_ids
        return super(HrPayrollAccountPartner, self).generate_line_center_cost(
            employee_center_costs, salary_rule,
            paylip_line, date, move_id, partner,
            move, slip)

    # Lines without center cost and parafiscal
    def _lines_without_ccp(self, salary_rule, paylip_line, move, slip, partner,
                           date, employee_center_costs):
        line_ids = []
        if paylip_line.payroll_news_id:
            for payroll_news_id in paylip_line.payroll_news_id:
                employee_payroll_news = self.get_employee_news(
                    slip, payroll_news_id)
                context = dict(self._context,
                               total_by_news=(
                                   employee_payroll_news.total *
                                   self._get_validate_sign_value(
                                       paylip_line.rate)))
                line_ids += super(HrPayrollAccountPartner,
                                  self.with_context(context)
                                  )._lines_without_ccp(
                                      salary_rule, paylip_line, move, slip,
                                      partner, date, employee_center_costs)
            return line_ids
        return super(HrPayrollAccountPartner, self)._lines_without_ccp(
            salary_rule, paylip_line, move, slip, partner, date,
            employee_center_costs)
