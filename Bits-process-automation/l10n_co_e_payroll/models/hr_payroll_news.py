# Part of Bits. See LICENSE file for full copyright and licensing details.
import logging
from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.tools import float_round
from odoo.tools.misc import format_date
from datetime import datetime
from calendar import monthrange
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class HrPayrollNewsInherit(models.Model):
    _inherit = 'hr.payroll.news'

    datetime_start = fields.Datetime('Start date', store=True)
    datetime_end = fields.Datetime('End date', store=True)
    check_hour_extra = fields.Boolean()
    check_range_date = fields.Boolean()

    @api.onchange('salary_rule_id')
    def _compute_check_hour_extra(self):
        for record in self:
            if record.salary_rule_id.code in ['60', '65', '70', '75']:
                record.check_hour_extra = True
            else:
                record.check_hour_extra = False

    @api.onchange(
                    'datetime_start',
                    'datetime_end',
                    'employee_payroll_news_ids'
                )
    def calculate_hours_time(self):
        for record in self:
            if record.datetime_end and record.datetime_start:
                if record.datetime_start < record.datetime_end:
                    record.check_range_date = False
                    diference_time = record.datetime_end\
                        - record.datetime_start
                    days = (diference_time.days)*24 or 0.0
                    hours = (diference_time.seconds)/3600 or 0.0
                    total_hours = days + hours
                    if record.employee_payroll_news_ids:
                        for employee in record.employee_payroll_news_ids:
                            employee.quantity = total_hours
                    else:
                        return False

                else:
                    record.check_range_date = True
                    for employee in record.employee_payroll_news_ids:
                            employee.quantity = 0.00
