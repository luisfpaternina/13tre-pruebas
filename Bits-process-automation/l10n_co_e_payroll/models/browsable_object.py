# -*- coding: utf-8 -*-

from calendar import month
from odoo.tools import formatLang
from pytz import timezone
from datetime import datetime
from odoo import fields
import calendar


from odoo.addons.hr_payroll.models.browsable_object\
    import Payslips


class Payslips(Payslips):

    def _generate_date(self, format):
        return fields.Datetime.now().strftime(format)

    def days_360(self, date1, date2):
        if not date1 or not date2:
            return 0
        start_day = date1.day
        end_day = date2.day

        if start_day == 31:
            start_day = 30

        if end_day == 31:
            end_day = 30

        days_diff = (date2.year - date1.year) * 360
        days_diff += (date2.month - date1.month) * 30
        days_diff += (end_day - start_day) + 1

        return days_diff

    def _get_contract_date_end(self):
        field_elem = ''
        settlement_id = self.dict._get_settlement()
        if settlement_id and settlement_id.date_payment:
            date_from = fields.Datetime.from_string(self.dict.date_from).date()
            date_to = fields.Datetime.from_string(self.dict.date_to).date()
            date_payment = fields.Datetime.from_string(
                settlement_id.date_payment)
            field_elem = date_payment.strftime('%Y-%m-%d') \
                if date_from <= date_payment.date() <= date_to else ''
        return field_elem

    def _get_all_worked_days(self, date_start, date_end):
        settlement_id = self.dict._get_settlement()
        if settlement_id and settlement_id.date_payment:
            date_end = fields.Datetime.from_string(
                settlement_id.date_payment).date()
        return self.days_360(date_start, date_end)

    # Function to get information for health and pension salary rules
    # for payslips electronic invoicing
    #
    # self: BrowsableObject(hr_payroll)
    #
    def _get_health_pension_value(self):
        payslip = self.dict
        if payslip:
            health_value = 0
            pension_value = 0
            for line in payslip.line_ids:
                salary_rule_type = line.salary_rule_id.l10n_type_rule
                if salary_rule_type == 'health':
                    health_value += abs(line.total)
                if salary_rule_type == 'pension_fund':
                    pension_value += abs(line.total)
            checked_payslip = [payslip.id]
            for emp_payslip in payslip.employee_id.slip_ids:
                if (emp_payslip.struct_id.name == "Vacaciones"
                and not emp_payslip.id in checked_payslip
                and emp_payslip.date_from <= payslip.date_to
                and emp_payslip.date_to >= payslip.date_from
                and emp_payslip.state not in ['cancel']):
                    for line in emp_payslip.line_ids:
                        salary_rule_type = line.salary_rule_id.l10n_type_rule
                        if salary_rule_type == 'health':
                            health_value += abs(line.total)
                        if salary_rule_type == 'pension_fund':
                            pension_value += abs(line.total)
                    checked_payslip.append(emp_payslip.id)
            
            return health_value, pension_value


    # Function to separate integer part for decimal part in float numbers
    #
    # value: Integer or String - Complete number
    # decimals: Quantity of decimals required
    def truncate_decimals(self, value, decimals):
        
        if type(value) == str:
            value = float(value)
        if value < 0:
            value = abs(value)
        
        split_value = str(value).split(".")
        if len(split_value) > 1:
            txt = split_value[1][:decimals]
        else: 
            txt = '0'
        if len(txt) == decimals:
            txt = txt
        else:
            txt = str(txt) + ('0' * (decimals - 1))

        return int(value), int(txt)
    
    # Function to round value using DIAN round method (half_to_even)
    #
    # int_value: Integer part
    # dec_value: Decimal part
    def round_value_dian(self, int_value, dec_value):

        if dec_value >= 60:
            int_value += 1
        elif dec_value >= 50 and dec_value < 60 and dec_value % 2 != 0:
            int_value += 1

        return int_value

    def datetime_now_user_tz(self):
        date_now = fields.datetime.now()
        dt_format = "%Y-%m-%d %H:%M:%S"
        tz = self.env.user.tz
        date_user_tz = date_now.astimezone(timezone(tz))
        date_user_tz = date_user_tz.strftime(dt_format)

        return date_user_tz

    def update_tz(self, date_now):
        dt_format = "%Y-%m-%d %H:%M:%S"
        tz = self.env.user.tz
        date_user_tz = date_now.astimezone(timezone(tz))
        date_user_tz = date_user_tz.strftime(dt_format)

        return date_user_tz
    
    # Get quantity affected to round totals
    #
    # return total difference between rounded and original value
    def _get_totals_round_value(self):
        payslip = self.dict
        if payslip:
            total_round = 0.0
            total_pay_ori = 0
            total_pay_rounded = 0
            total_ded_ori = 0
            total_ded_rounded = 0
            total_acc_ori = 0
            total_acc_rounded = 0
            for line in payslip.line_ids:
                if (line.salary_rule_id and 
                line.salary_rule_id.l10n_type_rule == 'total_payslip'):
                    total_pay_ori = abs(line.total)
                    intv, decv = payslip.truncate_decimals(total_pay_ori, 2)
                    total_pay_rounded = (
                        payslip.round_value_dian(intv, decv)
                    )
                    if total_pay_ori > total_pay_rounded:
                        total_round += total_pay_ori - total_pay_rounded
                    else:
                        total_round += total_pay_rounded - total_pay_ori
                elif line.category_id.code == 'DED':
                    total_ded_ori += abs(line.total)
                    intv, decv = payslip.truncate_decimals(total_ded_ori, 2)
                    total_ded_rounded = (
                        payslip.round_value_dian(intv, decv)
                    )
                elif (line.salary_rule_id and 
                line.salary_rule_id.l10n_type_rule == 'total_accrual'):
                    total_acc_ori = abs(line.total)
                    intv, decv = payslip.truncate_decimals(total_acc_ori, 2)
                    total_acc_rounded = (
                        payslip.round_value_dian(intv, decv)
                    )
                    if total_acc_ori > total_acc_rounded:
                        total_round += total_acc_ori - total_acc_rounded
                    else:
                        total_round += total_acc_rounded - total_acc_ori
                
            if total_ded_ori and total_ded_rounded:
                if total_ded_ori > total_ded_rounded:
                    total_round += total_ded_ori - total_ded_rounded
                else:
                    total_round += total_ded_rounded - total_ded_ori

            return round(total_round, 2)
    
    def get_date_end_employee(self):
        date_end = self.contract_id.date_end or ''
        return date_end

    def get_date_start_employee(self):
        date_start = self._get_recursive_contract_end(self.contract_id)
        return date_start

    def _get_recursive_contract_end(self, contract_id):
        date_start = contract_id.date_start.replace(day=1)
        day_end_month = calendar.monthrange(date_start.year, date_start.month)[-1]
        date_end = contract_id.date_end or date_start.replace(day=day_end_month)
        contract_ids = self.env['hr.contract'].search([
            ('date_start','<=',date_start),
            ('date_end','>=',date_end),
            ('state','=','cancel'),
            ('employee_id','=',self.employee_id),
            ('id','!=',self.contract_id.id)])
            
        for contract in contract_ids:
            if contract.date_start < date_start:
                date_start = contract.date_start
        return date_start
