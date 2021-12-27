# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_round
from calendar import month, monthrange, calendar
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from .hr_payroll_holidays_payslip import (MyHolidayPayslip)
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject


class HrPayrollHolidaysHistory(models.Model):
    _name = 'hr.payroll.holidays.history'
    _description = _('module for the respective vacation settlement process')

    name = fields.Char(required=True)
    employee = fields.Many2one(
        'hr.employee',
        string="Employee",
        required=True
    )
    only_compensated_days = fields.Boolean('You will have only compensated days')
    holiday_lapse = fields.Many2one(
        'hr.payroll.holiday.lapse',
        required=True,
        domain="[('employee_id', '=', employee)]")
    enjoyment_start_date = fields.Date('Enjoyment start date')
    enjoyment_end_date = fields.Date('Enjoyment end date')
    enjoyment_days = fields.Float(
        digits=(32, 2), string="Enjoyment days"
    )

    # enjoyment days current month
    enjoyment_current_month = fields.Float(
        digits=(32, 2),
        string='Days month')
    enjoyment_next_month = fields.Float(
        digits=(32, 2),
        string='Days next month')

    compensated_days = fields.Float(
        digits=(32, 2), string="Compensated days"
    )
    payment_date = fields.Date('Payments date', required=True)
    settlement_month = fields.Char('Settlement month')
    year = fields.Char()
    liquidated_period = fields.Selection(
        [
            ('month', 'Monthly'),
            ('biweekly', 'Biweekly')
        ], string="Liquidated period", required=True
    )
    holidays_current_month = fields.Float(
        digits=(32, 2), string='Holidays current month')
    holidays_next_month = fields.Float(
        digits=(32, 2), string='Holidays next month')
    holidays = fields.Float(
        digits=(32, 2), string='Holidays',
        compute='_get_work_days_employee'
    )

    is_complete = fields.Boolean('Completed')
    state = fields.Char()
    document = fields.Binary()
    comments = fields.Char()
    payroll_news_ids = fields.One2many(
        'hr.payroll.news',
        'holiday_history_id',
        string='Payroll News')

    global_state = fields.Selection(
        [('draft', 'Draft'),
         ('approval', 'Approval')],
        'Status', copy=False, default='draft')

    # Validaciones de formulario
    def _validation_fields(self, history, lapse):
        res_company = self.env.company

        if not history.get('enjoyment_days') > 0:
            raise ValidationError(
                _('The days of enjoyment must be greater than 0')
            )

        if history.get('enjoyment_days') < res_company.minimum_days_enjoyed:
            raise ValidationError(
                _('You can only enjoy {0} days minimum').format(
                    res_company.minimum_days_enjoyed))

        days_per_period = lapse._get_days_per_period(
            history.get('employee'), lapse.begin_date)

        if history.get('enjoyment_days') > days_per_period:
            raise ValidationError(
                _('You cannot enjoy more than {0} days').format(
                    days_per_period))

        # Se valida que los dias compensados no puedan ser
        # mayor de 8
        if (history.get('compensated_days') >
                res_company.maximum_days_compensated):
            raise ValidationError(
                _('The compensated days cannot be more than %s') %
                res_company.maximum_days_compensated
            )

        # Se validan si la suma entre los dias tomados del periodo,
        # los dias disfrutados del historico
        # y los dias compensados sea menos de 15
        if (history.get('enjoyment_days') +
                history.get('compensated_days') +
                lapse.days_taken +
                lapse.compesated_in_money) > days_per_period:
            raise ValidationError(
                _('The current period has {0} days to enjoy')
                .format(days_per_period - (
                    lapse.days_taken + lapse.compesated_in_money))
            )

    def _find_salary_rule(self, r_code):
        return self.env['hr.salary.rule'].search([
            ('code', '=', r_code)
        ], limit=1)

    def _get_conf_rule_as_novelty(self, r_code):
        dict_dates = {
            '145': {
                'current_month_payroll': 0,
                'lapse_month': 0
            },
            '145-1': {
                'current_month_payroll': 0,
                'lapse_month': 1
            },
            '146': {
                'current_month_payroll': 0,
                'lapse_month': 0
            },
            '146-1': {
                'current_month_payroll': 0,
                'lapse_month': 1
            },
            '147': {
                'current_month_payroll': 0,
                'lapse_month': 0
            },
            '148': {
                'current_month_payroll': 1,
                'lapse_month': 1
            },
            '148-1': {
                'current_month_payroll': 1,
                'lapse_month': 1
            }
        }

        r_dict = dict_dates.get(r_code)
        return r_dict['current_month_payroll'], r_dict['lapse_month']

    def _get_title_novelty(self, r_code, val):
        dict_template = {
            '145': _('Holidays %s') % val,
            '145-1': _('Holidays next month %s') % val,
            '146': _('Festive holidays %s') % val,
            '146-1': _('Festive holidays next month %s') % val,
            '147': _('Money Vacation %s') % val,
            '148': _('Advance days vacation next month %s') % val,
            '148-1': _('Advance holidays next month %s') % val
        }

        return dict_template.get(r_code)

    def _get_quantity_by_rule(self, r_code):
        dict_quantity = {
            '145': self.enjoyment_current_month,
            '145-1': self.enjoyment_next_month,
            '146': self.holidays_current_month,
            '146-1': self.holidays_next_month,
            '147': self.compensated_days,
            '148': self.enjoyment_next_month,
            '148-1': self.holidays_next_month
        }

        return dict_quantity.get(r_code)

    # Creación de historial de vacaciones
    # @api.model_create_multi
    @api.model
    def create(self, history):
        lapse = self.env[
            'hr.payroll.holiday.lapse'
        ].browse(history.get('holiday_lapse'))

        if history.get('only_compensated_days') == False:
        # for history in vals:
            if history.get('enjoyment_days') == False:
                self._validation_fields(history, lapse)
                histories = self.env['hr.payroll.holidays.history'].search([
                    ('employee', '=', history.get('employee'))
                ])

                start_date = datetime.strptime(history.get(
                    'enjoyment_start_date'), '%Y-%m-%d').date()
                end_date = datetime.strptime(history.get(
                    'enjoyment_end_date'), '%Y-%m-%d').date()

                history_repeat = histories.filtered(
                    lambda item: (item.enjoyment_start_date <= start_date and
                                item.enjoyment_end_date >= start_date) or
                    (item.enjoyment_start_date <= end_date and
                    item.enjoyment_end_date >= end_date))

                if history_repeat:
                    raise ValidationError(
                        _("""a vacation history already exists """
                        """for the employee in the same time period"""))

        # Se crea historico de vacaciones
        history['name'] = '{0} periodo {1}/{2}'.format(
            lapse.employee_id.name,
            lapse.begin_date,
            lapse.end_date)
        # Se crean novedades de vacaciones del empleado
        history_created = super(HrPayrollHolidaysHistory, self).create(history)

        return history_created

    @api.onchange('employee', 'enjoyment_start_date', 'enjoyment_end_date')
    @api.constrains('employee')
    def _get_work_days_employee(self):
        for record in self:
            if record.only_compensated_days == True:
                record.enjoyment_start_date= False
                record.enjoymen_end_date= False
                record.holidays = False
                record.enjoyment_days = 0
            if (record.enjoyment_start_date
                    and record.enjoyment_end_date and record.employee):
                record.enjoyment_days = record._get_calendar_employee_days(
                    record.enjoyment_start_date,
                    record.enjoyment_end_date,
                    'enable')

                record.holidays = record._get_calendar_employee_days(
                    record.enjoyment_start_date,
                    record.enjoyment_end_date,
                    'disable')

                if (record.enjoyment_start_date.month <
                    record.enjoyment_end_date.month or
                    (record.enjoyment_start_date.month >
                        record.enjoyment_end_date.month and
                        record.enjoyment_start_date.year <
                        record.enjoyment_end_date.year)):
                    # Se optiene el numero de dias del mes
                    number_days_month = record._get_number_days_month(
                        record.enjoyment_start_date.year,
                        record.enjoyment_start_date.month
                    )
                    # Se modifica diccionario para establecer el
                    # mes de los dias disfrutados
                    record.enjoyment_current_month = record\
                        ._get_calendar_employee_days(
                            record.enjoyment_start_date,
                            record.enjoyment_start_date +
                            relativedelta(day=number_days_month),
                            'enable')

                    record.enjoyment_next_month = (
                        record._get_calendar_employee_days(
                            record.enjoyment_end_date + relativedelta(day=1),
                            record.enjoyment_end_date,
                            'enable'))

                    record.holidays_current_month = (
                        record._get_calendar_employee_days(
                            record.enjoyment_start_date,
                            record.enjoyment_start_date +
                            relativedelta(day=number_days_month),
                            'disable'))

                    record.holidays_next_month = (
                        record._get_calendar_employee_days(
                            record.enjoyment_end_date + relativedelta(day=1),
                            record.enjoyment_end_date,
                            'disable'))
                else:
                    record.enjoyment_next_month = 0
                    record.holidays_next_month = 0
                    record.enjoyment_current_month = record.enjoyment_days
                    record.holidays_current_month = (
                        record._get_calendar_employee_days(
                            record.enjoyment_start_date,
                            record.enjoyment_end_date,
                            'disable'))
                # Recalculate 30 day
                difference_days = record.difference_validator()
                record.holidays_current_month += difference_days if\
                    difference_days else 0
                record.holidays += difference_days if difference_days else 0

    # Cuenta dias habiles del mes, usa el calendario del empleado
    def _get_calendar_employee_days(self, start_date, end_date, enable):
        date_from = fields.Datetime.from_string(start_date)
        date_to = fields.Datetime.from_string(end_date)
        date_to = date_to.replace(hour=23, minute=59)

        if enable == 'enable':
            return self.employee._get_work_days_data(
                date_from, date_to)['days']

        return self.employee._get_leave_days_data(date_from, date_to)['days']

    # Calcula regla salarial para calcular amount
    def _amount_compute_rule(self, employee, salary_rule):

        contract = employee.contract_id
        if not contract:
            raise ValidationError(
                _('The employee must have an active contract')
            )

        localdict = {
            **{'float_round': float_round},
            **{
                'employee': employee,
                'contract': contract,
                'holiday': MyHolidayPayslip(employee.id, self, self.env)
            }
        }
        localdict.update({
            'result': None,
            'result_qty': 1.0,
            'result_rate': 100
        })
        amount, qty, rate = salary_rule._compute_rule(localdict)
        tot_rule = amount * qty * rate / 100.0
        if salary_rule.l10n_type_rule == 'compensated_holidays':
            amount = (contract.wage)/30
            qty = 1
            tot_rule = amount * qty * rate / 100.0

        return tot_rule

    # Prepara listado de novedades de vacaciones
    def _prepare_holiday_news(self):
        employee_holiday_news = []
        codes_salary_rule = ['145', '145-1',
                             '146', '146-1', '147', '148', '148-1']

        for sr_code in codes_salary_rule:
            if not self._get_quantity_by_rule(sr_code) > 0:
                continue

            salary_rule = self._find_salary_rule(sr_code)
            novelty = self._create_holiday_new(
                self._get_title_novelty(sr_code, self.employee.name),
                salary_rule)

            employee_holiday_news.append(novelty)

        if self.only_compensated_days == True:
            for holiday in employee_holiday_news:
                if holiday['l10n_type_rule'] == 'compensated_holidays':
                    employee_holiday_news = holiday
                    break

        return employee_holiday_news
    
    def _create_holiday_new(self, title, salary_rule):

        if self.only_compensated_days == False:
            _structure = salary_rule.struct_id
            _date_start, _date_end, \
                _request_date_from, _request_date_to = self._get_dates_novelty(
                    salary_rule)

            _amount = self._amount_compute_rule(
                self.employee, salary_rule)
        else:
            month_payment = self.payment_date.month
            year_payment = self.payment_date.year
            last_day_of_month = monthrange(year_payment,month_payment)[1]
            _request_date_from = datetime(year_payment,month_payment,1)
            _request_date_to = datetime(year_payment,month_payment,last_day_of_month)
            _date_start = datetime(year_payment,month_payment,1) 
            _date_end = datetime(year_payment,month_payment,last_day_of_month)
            _structure = salary_rule.struct_id
            contract = self.employee.contract_id
            employee = self.employee
            localdict = {
                **{'float_round': float_round},
                **{
                    'employee': employee,
                    'contract': contract,
                    'holiday': MyHolidayPayslip(employee.id, self, self.env)
                }
            }
            localdict.update({
                'result': None,
                'result_qty': 1.0,
                'result_rate': 100
            })
            amount, qty, rate = salary_rule._compute_rule(localdict)
            amount = (contract.wage)/30
            qty = 1
            _amount = amount * qty * rate / 100.0

        if salary_rule.code in ['146-1']:
            _amount = (self.employee.contract_id.wage)/30 * self._get_quantity_by_rule(salary_rule.code)

        payroll_new_line = {
            'employee_id': self.employee.id,
            'amount': _amount,
            'quantity': self._get_quantity_by_rule(salary_rule.code)
        }
        return dict(
            name=title,
            request_date_from=_request_date_from,
            request_date_to=_request_date_to,
            date_start=_date_start,
            date_end=_date_end,
            payroll_structure_id=_structure.id,
            salary_rule_id=salary_rule.id,
            l10n_type_rule = salary_rule.l10n_type_rule,
            holiday_history_id=self.id,
            employee_payroll_news_ids=[[
                0, 0, payroll_new_line
            ]]
        )

    def _get_dates_novelty(self, s_rule):
        p_month, l_month = self._get_conf_rule_as_novelty(
            s_rule.code)

        date_start = self.payment_date + relativedelta(day=1, months=+p_month)
        date_end = self.payment_date + relativedelta(
            day=self._get_number_days_month(
                self.payment_date.year, self.payment_date.month),
            months=+p_month)

        request_date_from = self.payment_date + relativedelta(
            day=(1 if l_month == 1 else self.enjoyment_start_date.day),
            months=+l_month)

        request_date_to = self.payment_date + relativedelta(
            day=(self.enjoyment_end_date.day
                 if l_month == 1 else date_end.day),
            months=+l_month
        )

        return date_start, date_end, request_date_from, request_date_to

    # obtiene el ultimo dia del mes

    def _get_number_days_month(self, year, month):
        return monthrange(year, month)[1]

    def create_holiday_news(self):
        commands = [(
            2, line_id.id, False) for line_id in self.payroll_news_ids]
        holiday_news = self._prepare_holiday_news()
        new_records = self.env['hr.payroll.news'].create(holiday_news)
        for record in new_records:
            commands.append((4, record.id))
        return self.write({'payroll_news_ids': commands})

    def approve_holiday_history(self):
        lapse = self.env[
            'hr.payroll.holiday.lapse'
        ].browse(self.holiday_lapse.id)

        # Validate novelties
        if not self.payroll_news_ids:
            raise ValidationError(
                _('Must first calculate the sheet.')
            )
        else:
            stage_approval = self.env['hr.payroll.news.stage'].search([('sequence','=',2)])
            for line_holidays in self.payroll_news_ids:
                if line_holidays.salary_rule_id.code not in ['148','148-1']:
                    line_holidays.write({'stage_id': stage_approval.id})




        # Se debe actualizar los dias tomados en el periodo
        pending_days = (
            lapse.pending_days -
            (self.enjoyment_days +
             self.compensated_days))

        lapse.write({
            'days_taken': (
                lapse.days_taken + self.enjoyment_days),
            'pending_days': pending_days,
            'compesated_in_money': (
                lapse.compesated_in_money + self.compensated_days
            ),
            'state': '3' if pending_days == 0 else lapse.state
        })

        self.global_state = "approval"
        return True

    def cancel_holiday_history(self):
        lapse = self.env[
            'hr.payroll.holiday.lapse'
        ].browse(self.holiday_lapse.id)

        # Validate liquided novelties
        noveltys = self.payroll_news_ids
        for novelty in noveltys:
            if novelty.stage_id.is_won:
                raise ValidationError(
                    _('Once payroll news is in Liquidated state, It\'' +
                        's not allowed to continue.')
                )

        # Se debe actualizar los dias tomados en el periodo
        pending_days = (
            lapse.pending_days +
            (self.enjoyment_days +
             self.compensated_days))

        lapse.write({
            'days_taken': (
                lapse.days_taken - self.enjoyment_days),
            'pending_days': pending_days,
            'compesated_in_money': (
                lapse.compesated_in_money - self.compensated_days
            ),
            'state': '2'
        })

        # Change status history
        self.global_state = "draft"

        # Delete novelties
        commands = [(
            2, line_id.id, False) for line_id in self.payroll_news_ids]
        return self.write({'payroll_news_ids': commands})

    def difference_validator(self):
        date_from = self.enjoyment_start_date
        max_day_in_month = monthrange(
            date_from.year, date_from.month)[1]
        max_day_in_selected = self.enjoyment_end_date.day
        if (self.enjoyment_next_month or self.holidays_next_month or
                max_day_in_month == max_day_in_selected):
            day = date(date_from.year, date_from.month, max_day_in_month)
            if (max_day_in_month == 31 or max_day_in_month == 29):
                return self.difference_calculator([day], max_day_in_month)
            elif max_day_in_month == 28:
                return self.difference_calculator([day, day], max_day_in_month)
        else:
            return 0

    def difference_calculator(self, days, max_day_in_month):
        amount_days = 0
        for day in days:
            dynamic_value = -1 if max_day_in_month > 30 else 1
            amount_days += dynamic_value
        return amount_days

    def validate_holiday(self, date):
        init_day = datetime(date.year, date.month, date.day, 0, 0, 0)
        end_day = datetime(date.year, date.month, date.day, 23, 59, 59)
        holidays = self.env["resource.calendar.leaves"].search([
            ('date_from', '>=', init_day),
            ('date_from', '<=', end_day)
        ])
        result = True if holidays else False
        return result
