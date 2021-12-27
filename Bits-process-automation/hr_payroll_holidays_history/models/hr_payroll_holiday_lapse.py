from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from datetime import date, timedelta
from calendar import monthrange


class HrPayrollHolidayLapse(models.Model):
    _name = 'hr.payroll.holiday.lapse'
    _description = _('Manages the vacation periods of the collaborators')

    name = fields.Char(required=True)
    begin_date = fields.Date(string='Begin date', required=True)
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True
    )
    end_date = fields.Date(string='End date', required=True)
    number_holiday_days = fields.Float(
        digits=(32, 2),
        string='Number holiday days')
    days_taken = fields.Float(
        digits=(32, 2),
        string='Days taken')
    compesated_in_money = fields.Float(
        digits=(32, 2),
        string='Compesated in money')
    pending_days = fields.Float(
        digits=(32, 2),
        string='Pending days')
    type_vacation = fields.Selection([
        ('normal', 'Normal'),
        ('integral', 'Integral'),
        ('electiva', 'Sena electiva'),
        ('practica', 'Sena practica')
    ], string='Tipo de vacaciones', required=True)
    document = fields.Char(string='Document')
    comments = fields.Char(string='Comments')
    state = fields.Selection([
        ('1', 'Calculating vacations'),
        ('2', 'Active'),
        ('3', 'Liquidated')
    ], string='State', required=True)
    holidays_history_ids = fields.One2many(
        'hr.payroll.holidays.history',
        'holiday_lapse',
        string="Holiday history"
    )
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company, required=True)

    # Funcion que calcula el periodo de vacaciones de los empleado
    def _create_holiday_lapse(self):
        begin_date = False
        # se consultan todos los empleados, con contrato en estado abierto
        employees = self.env['hr.employee'].search([
            ('contract_id', '!=', False),
            ('contract_id.state', '=', 'open')
        ])

        for employee in employees:
            contract = employee.contract_id
            if employee.holidays_ids:
                current_period = self.search([
                    ('state', '=', '1'),
                    ('employee_id', '=', employee.id)
                ], limit=1)

                if current_period:
                    if date.today() <= current_period.end_date:
                        avalaibe_days = self._calcule_avalaible_days(
                            employee.id,
                            current_period.begin_date,
                            (contract.date_end if contract.date_end
                                else current_period.end_date)
                        )

                        current_period.write({
                            'number_holiday_days': avalaibe_days,
                            'pending_days': (
                                avalaibe_days -
                                (current_period.days_taken +
                                 current_period.compesated_in_money))
                        })
                    else:
                        current_period.write({
                            'state': '3' if
                            current_period.pending_days == 0
                            else '2'
                        })
                        begin_date = (
                            current_period.end_date + timedelta(days=1))

                        self._prepare_holiday_lapse(
                            employee, begin_date)

            else:
                self._prepare_holiday_lapse(
                    employee, contract.date_start, contract.date_end)

    # Función que prepara holiday lapse
    def _prepare_holiday_lapse(self, employee, begin_date, end_date=False):
        isFixed = end_date if not end_date else True
        structure_type = employee.contract_id.structure_type_id

        if not end_date:
            end_date = (
                date(
                    begin_date.year + 1,
                    begin_date.month,
                    begin_date.day
                )
                + timedelta(days=-1)
            )

        avalaibe_days = self._calcule_avalaible_days(
            employee.id,
            begin_date, end_date, isFixed)

        type_vacation = ''
        if structure_type.name and 'integral' in structure_type.name.lower():
            type_vacation = 'integral'
        elif structure_type.name and 'normal' in structure_type.name.lower():
            type_vacation = 'normal'
        else:
            return False

        line = {
            'name': '{0}, periodo {1}/{2}'.format(
                employee.name,
                begin_date,
                end_date
            ),
            'employee_id': employee.id,
            'begin_date': begin_date,
            'end_date': end_date,
            'number_holiday_days': avalaibe_days,
            'pending_days': avalaibe_days,
            'type_vacation': type_vacation,
            'state': '2' if avalaibe_days >= 15 or isFixed else '1'
        }
        self.create(line)

        if end_date < date.today() and not isFixed:
            self._prepare_holiday_lapse(
                employee, end_date + timedelta(days=1))

        return line

    # Funcion que calcula los dias disponibles
    def _calcule_avalaible_days(self,
                                employee_id, begin_date, end_date,
                                is_fixed=False):

        days_per_period = self._get_days_per_period(employee_id, begin_date)
        today = date.today()

        if today < end_date and not is_fixed:
            calculate_days = self._days_360(begin_date, today)
            return ((
                (calculate_days if calculate_days <= 360 else 360) / 30)
                * (days_per_period/12))

        calculate_days = self._days_360(begin_date, end_date)
        return (((calculate_days if calculate_days <= 360 else 360) / 30)
                * (days_per_period/12))

    def _get_days_per_period(self, employee_id, begin_date):
        res_company = self.env.company

        count_periods = self.search_count([
            ('employee_id', '=', employee_id),
            ('begin_date', '<', begin_date)
        ])

        if count_periods >= res_company.after_x_lapse:
            return res_company.days_per_period + res_company.additional_days

        return res_company.days_per_period

    def _days_360(self, start_date, end_date):
        start_day = start_date.day
        start_month = start_date.month
        start_year = start_date.year
        end_day = end_date.day
        end_month = end_date.month
        end_year = end_date.year

        if start_day == 31 or self._is_last_day_february(start_date):
            start_day = 30

        if start_day == 30 and end_day == 31:
            end_day = 30

        return (((end_year - start_year) * 360) +
                ((end_month - start_month) * 30) +
                (end_day - start_day)) + 1

    def _is_last_day_february(self, date):
        return (date.month == 2
                and date.day == monthrange(date.year, date.month)[1])

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            employee = self.env['hr.employee'].browse(vals.get('employee_id'))
            vals['name'] = '{0}, periodo {1}/{2}'.format(
                employee.name,
                vals.get('begin_date'),
                vals.get('end_date')
            )

        return super(HrPayrollHolidayLapse, self).create(vals)
