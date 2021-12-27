# Part of Bits. See LICENSE file for full copyright and licensing details.

from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from calendar import monthrange
from odoo import api, fields, models, _
from odoo.tools import float_round
from collections import defaultdict
from odoo.addons.hr_payroll.models.browsable_object \
    import BrowsableObject, InputLine, WorkedDays, Payslips


class MyPayslips(BrowsableObject):

    def get_total_holidays(self):
        # TODO traer esta informacion desde el libro de vacaciones
        return (1.25*12)

    # TODO se comentarean, estas funciones no son usadas
    # def get_business_days(self):
    #     # TODO traer esta informacion desde el libro de vacaciones
    #     return 8

    # def get_holidays(self):
    #     # TODO traer esta informacion desde el libro de vacaciones
    #     return 7

    def get_period_month(self, from_date, to_date, month=6):
        return (bool)(from_date.month == month and to_date.month == month)

    def sum_payslip_line(self, code, from_date, to_date, state=['done']):
        self.env.cr.execute("""
            SELECT sum(case when hp.credit_note = False then (pl.total)
            else (-pl.total) end),
            count(hp.id) as payslip_count
            FROM hr_payslip as hp, hr_payslip_line as pl
            WHERE hp.employee_id = %s AND hp.state IN %s
            AND hp.date_from >= %s AND hp.date_to <= %s AND
            hp.id = pl.slip_id AND pl.code = %s""", (
            self.employee_id, tuple(state), from_date, to_date, code))
        return self.env.cr.fetchone()

    def _sum(self, code, from_date, to_date, state=['done']):
        self.env.cr.execute("""
            SELECT sum(pi.amount) as total,
            sum(pi.number_of_days) as number_of_days,
            count(hp.id) as payslip_count
            FROM hr_payslip as hp, hr_payslip_worked_days as pi,
            hr_work_entry_type as wet
            WHERE hp.employee_id = %s AND hp.state IN %s
            AND hp.date_from >= %s AND hp.date_to <= %s AND
            hp.id = pi.payslip_id AND pi.work_entry_type_id = wet.id
            AND wet.code = %s""", (self.employee_id, tuple(state),
                                   from_date, to_date, code))
        return self.env.cr.fetchone()

    def sum(self, code, from_date, to_date, state=['done']):
        return self._sum(code, from_date, to_date, state)

    def _get_payroll_news_ids(self, from_date, to_date):
        return self.env['hr.employee.payroll.news'].search(
            [('employee_id', '=', self.employee_id),
             ('payroll_news_id.date_start', '>=', from_date),
             ('payroll_news_id.date_end', '<=', to_date),
             '|', ('payroll_news_id.stage_id.is_approved', '=', True),
             ('payroll_news_id.stage_id.is_won', '=', True)])

    def _get_contract_history(self, from_date, to_date):
        return self.env['hr.contract.history'].search([
            ('_type', '=', 'wage'),
            ('contract_id', '=', self.contract_id.id),
            ('adjusment_date', '>=', from_date),
            ('adjusment_date', '<=', to_date)
        ])

    def _get_sum_provisions(self, date_from, date_to):
        total_provisions = 0
        iteration = range(date_from.month, date_to.month + 1)

        for it in iteration:
            payslip = self.env['hr.payslip'].search([
                ('date_from', '<=', datetime.now().replace(month=it).date()),
                ('date_to', '>=', datetime.now().replace(month=it).date()),
                ('contract_id', '=', self.contract_id.id)
            ], limit=1)

            total_provisions += sum(
                x.total for x in
                payslip.line_ids.filtered(lambda x: x.code == 'PROCE'))

        return total_provisions
    
    def _get_rule_history(self, codes, states, from_date, date_to):
        rule_ids = self.env['hr.salary.rule'].search([('code','in',codes)])
        return self.env['hr.payslip.line'].search([
            ('slip_id.state', 'in', states),
            ('slip_id.date_from', '>=', from_date),
            ('salary_rule_id', 'in', rule_ids.ids),
            ('slip_id.contract_id','=',self.contract_id.id)
        ])
        
    def _get_avarage_salary(self, date_from, date_to):
        if not self.contract_id.contract_history_ids or len(self.contract_id.contract_history_ids) == 1:
            return self.contract_id.wage
        salary_line_ids = self.env['hr.contract.history'].search([
            ('contract_id', '=', self.contract_id.id),
            ('date','>=',date_from),
        ])
        date_fixes = [x.adjusment_date for x in salary_line_ids]
        dict_salary = {}
        for line_id in salary_line_ids:
            dict_salary[str(line_id.adjusment_date)] = line_id.amount
            for i in range(12-line_id.adjusment_date.month):
                date_next = line_id.adjusment_date + relativedelta(months=(i+1))
                if date_next in date_fixes:
                    continue
                dict_salary[str(date_next)] = line_id.amount
        total_amount = sum(dict_salary.values())
        total_months = len(dict_salary)
        avg_salary = total_amount / total_months
        return avg_salary

    def sum_provisions(self, code, codes, from_date, to_date, period=1,
                       days=360, percentage=100, percentage_rule=100):
        now_year = datetime.now().year
        month_init = 1 if (period == 1 or period == 3) else 7
        month_end = 7 if period == 1 else 1
        year = now_year + 1 if (period == 2 or period == 3) else now_year

        from_date_period = datetime.now().replace(
            day=1, month=month_init, year=now_year).date()
        to_date_period = datetime.now().replace(
            day=1, month=month_end, year=year).date()

        res = self.sum_payslip_line(code, from_date_period, to_date_period)
        tot_rule = res[0] and res[0] or 0.0

        # Current month
        tot_rule += self.compute_provisions(
            ['BASIC'], codes, from_date,
            to_date, percentage) * (percentage_rule/100)

        return tot_rule

    def sum_provisions_interest(self, code, codes, from_date,
                                to_date, period=1, days=360,
                                percentage=100, percentage_rule=100):
        now_year = datetime.now().year
        month_init = 1 if (period == 1 or period == 3) else 7
        month_end = 7 if period == 1 else 1
        year = now_year + 1 if (period == 2 or period == 3) else now_year

        from_date_period = datetime.now().replace(
            day=1, month=month_init, year=now_year).date()
        to_date_period = datetime.now().replace(
            day=1, month=month_end, year=year).date()

        res = self.sum_payslip_line(code, from_date_period, to_date_period)
        tot_rule = res[0] and res[0] or 0.0

        # Current month
        tot_rule += self.compute_provisions_severance_incremental(
            ['BASIC', '120'], codes, from_date, to_date, percentage_rule)
        return tot_rule

    def compute_holidays_pay(self, code, codes, from_date, to_date, days=30):
        from_date = datetime.now().replace(day=1, month=1).date()
        to_date = datetime.now().replace(day=31, month=12).date()

        # Current month information
        current = self.dict.get_worked_days_line_ids(code)
        tot_rule = current.amount if current.amount > 0 else 0.0
        worked_days = current.number_of_days \
            if current.number_of_days > 0 else 0

        # Traer datos del año
        worked_days = 360
        # Calculos adicionales Novedades
        if len(codes) > 0:
            payroll_news_ids = self._get_payroll_news_ids(from_date, to_date)
            code_ids = payroll_news_ids.filtered(
                lambda line: line.payroll_news_id.salary_rule_code in codes)
            # Horas Extras + Comisiones
            sum_total = sum([line.total for line in code_ids])
            tot_rule += (sum_total/worked_days)*days
        return (tot_rule/30)*self.get_total_holidays()

    def get_worked_year_days(self, code, from_date=None,
                             to_date=None, state=['done']):
        if from_date is None:
            from_date = datetime.now().replace(day=1, month=1).date()

        if to_date is None:
            to_date = datetime.now().replace(day=31, month=12).date()

        current = self.dict.get_worked_days_line_ids(code)
        worked_days = current.number_of_days \
            if current.number_of_days > 0 else 0
        res = self.sum(code, from_date, to_date, state)
        worked_days += res[1] and res[1] or 0.0
        return worked_days

    def compute_severance_pay_interest(self, code, codes, from_date,
                                       to_date, percentage=12,
                                       period=3, days=360):
        from_date = datetime.now().replace(day=1, month=1).date()
        if from_date < self.contract_id.date_start:
            from_date = self.contract_id.date_start
        tot_severance = self.compute_severance_pay(code, codes, period, days)
        worked_days = self.get_worked_year_days(code=code, from_date=from_date, to_date=to_date)
        return (tot_severance * worked_days * (percentage/100)) / days

    def compute_severance_pay(self, code, codes, period=3, days=360):
        from_date = datetime.now().replace(day=1, month=1).date()
        to_date = datetime.now().replace(day=31, month=12).date()
        # Calcular el periodo de cambio de sueldo
        today = datetime.now().replace(day=1, month=12).date()
        from_date_period = today - relativedelta(months=period)
        if from_date < self.contract_id.date_start:
            from_date = self.contract_id.date_start
        # Current month information
        payslip_count = 1
        current = self.dict.get_worked_days_line_ids(code)
        tot_rule = current.amount if current.amount > 0 else 0.0
        worked_days = current.number_of_days \
            if current.number_of_days > 0 else 0

        current_salary_period = tot_rule * period

        # La suma de los sueldos desde Dic al mes periodo
        # Calcular el periodo de cambio de sueldo
        res = self.sum(code, from_date_period, to_date)
        tot_salary_period = res[0] and res[0] or 0.0

        res = self.sum(code, from_date, to_date)
        worked_days += res[1] and res[1] or 0.0
        # Si hay variante en el sueldo en el periodo
        if tot_salary_period != current_salary_period:
            # Se tomará como base el promedio de lo devengado en el último
            # Año de servicio o en todo el tiempo servido si fuere
            # Menor de un año.
            tot_rule += res[0] and res[0] or 0.0
            payslip_count += res[2] and res[2] or 0.0

        # subsidio de transporte
        tot_help = self.dict.get_line_data(
            ['120'],
            fixed_days=30
        )
        if tot_help == 0:
            paramater_id = self.env['hr.payroll.parameter.retention'].search([('year','=',from_date.year)])
            if paramater_id:
                minimum_wage = paramater_id.minimum_wage
                minimum_wage_avg = minimum_wage * 2
                tot_avg = (tot_rule/worked_days) * 30
                if tot_avg < minimum_wage_avg:
                    tot_help = paramater_id.transportation_allowance

        # Promedio de todos/ultimo salario por (dias trabajados / 360)
        tot_severance = ((tot_rule/payslip_count) +
                         tot_help) * (worked_days/days)

        # Calculos adicionales Novedades
        if len(codes) > 0:
            payroll_news_ids = self._get_payroll_news_ids(from_date, to_date)
            code_ids = payroll_news_ids.filtered(
                lambda line: line.payroll_news_id.salary_rule_code in codes)
            # Horas Extras + Comisiones
            sum_total = sum([line.total for line in code_ids])
            tot_severance += ((sum_total/worked_days)*30) * (worked_days/days)

        return tot_severance

    # Old legal premium calculation function - replaced to count 
    # days from contract start date to premium end
    """ def compute_legal_premium(self, code, codes, period=1, days=360):
        now_year = datetime.now().year
        month_init = 1 if period == 1 else 7
        month_end = 7 if period == 1 else 1
        year = now_year if period == 1 else now_year + 1

        from_date = datetime.now().replace(
            day=1, month=month_init, year=now_year).date()
        to_date = datetime.now().replace(
            day=1, month=month_end, year=year).date()

        # Sueldo, dias trabajados en el mes
        res = self.sum('WORK100', from_date, to_date)
        tot_rule = res[0] and res[0] or 0.0
        worked_days = res[1] and res[1] or 0.0
        payslip_count = res[2] and res[2] or 0.0
        payroll_news_ids = self._get_payroll_news_ids(from_date, to_date)
        code_ids = payroll_news_ids.filtered(
            lambda line: line.payroll_news_id.salary_rule_code in codes)

        # Horas Extras + Comisiones
        sum_total = sum([line.total for line in code_ids])

        # Subsidio de transporte
        subsidio_t = self.dict.get_line_data(
            [code],
            fixed_days=30
        )
        # Tener en cuenta la culminacion de contrato
        # Informacion Mes actual
        current = self.dict.get_worked_days_line_ids('WORK100')
        tot_rule += current.amount if current.amount > 0 else 0
        worked_days += current.number_of_days if current.number_of_days else 0

        # Current month
        payslip_count += 1
        result = ((((tot_rule + sum_total)/payslip_count)+subsidio_t)
                  * (worked_days/days))
        return result """
    
    def compute_legal_premium(self, code, codes, period=1, days=360):

        payslip_class = self.env['hr.payslip']

        # Establecer fechas de inicio y fin de prima

        now_year = datetime.now().year
        month_init = 1 if period == 1 else 7
        month_end = 7 if period == 1 else 1
        year = now_year if period == 1 else now_year + 1

        from_date = datetime.now().replace(
            day=1, month=month_init, year=now_year).date()
        to_date = datetime.now().replace(
            day=1, month=month_end, year=year).date()
        if from_date < self.contract_id.date_start:
            from_date = self.contract_id.date_start
        if to_date > self.date_to:
            to_date = self.date_to + relativedelta(days=1)

        # Validacion para cambios de salario dentro del periodo de prima
        tot_rule = 0
        if self.contract_id.contract_history_ids:
            changes_by_month = {}
            for salary_change in self.contract_id.contract_history_ids:
                if salary_change.adjusment_date >= from_date:
                    adj_date = salary_change.adjusment_date
                    if str(adj_date.month) in changes_by_month:
                        changes_by_month[str(adj_date.month)].append(
                            salary_change
                        )
                    else:
                        changes_by_month[str(adj_date.month)] = [
                            salary_change
                        ]
            
            if period == 2:
                fd_month = from_date.month
                td_month = 13
            else:
                fd_month = from_date.month
                td_month = to_date.month
            
            months_count = 0
            values_b_month = {}
            for month in range(fd_month, td_month):
                months_count += 1
                month_key = str(month)
                if month_key in changes_by_month.keys():
                    if len(changes_by_month[month_key]) > 1:
                        
                        salary_change_ids = sorted(
                            changes_by_month[month_key], 
                            key=lambda x: x.adjusment_date
                        )
                        # FIRST PART OF MONTH
                        first_sc = salary_change_ids[0]
                        values_b_month[month_key] = {}
                        values_b_month[month_key]['first_value'] = (
                            month,
                            first_sc.last_salary
                        )
                        
                        #SECOND PART OF MONTH
                        lats_sc = salary_change_ids[-1]
                        values_b_month[month_key]['last_value'] = (
                            month,
                            lats_sc.amount
                        )

                        count = 0
                        for salary_change in salary_change_ids:
                            
                            if count + 1 < len(salary_change_ids):
                                next_sc_date = (
                                    salary_change_ids[count+1].adjusment_date
                                )

                            adj_date = salary_change.adjusment_date

                            if lats_sc == salary_change:
                                sc_start = adj_date
                                sc_end = adj_date.replace(day=30)
                                sc_days = payslip_class.days360(
                                    sc_start, 
                                    sc_end
                                ) + 1
                                sc_total = sc_days * (
                                    salary_change.amount/30
                                )

                                tot_rule += sc_total
                            elif first_sc == salary_change:
                                old_salary_tot = 0
                                if adj_date.day != 1:
                                    # FIRST PART OF MONTH
                                    date_start_old = adj_date.replace(day=1)
                                    old_salary_days = payslip_class.days360(
                                        date_start_old, 
                                        date_end_new
                                    )
                                    old_salary_tot = old_salary_days * (
                                        salary_change.last_salary/30
                                    )

                                #SECOND PART OF MONTH
                                date_end_act = adj_date.replace(
                                    day=next_sc_date.day
                                )
                                act_salary_days = payslip_class.days360(
                                    adj_date, 
                                    date_end_act
                                )
                                act_salary_tot = act_salary_days * (
                                    salary_change.amount/30
                                )

                                tot_rule += act_salary_tot + old_salary_tot
                            else:
                                sc_start = adj_date
                                sc_end = adj_date.replace(
                                    day=next_sc_date.day
                                )
                                sc_days = payslip_class.days360(
                                    sc_start, 
                                    sc_end
                                )
                                sc_total = sc_days * (
                                    salary_change.amount/30
                                )

                                tot_rule += sc_total
                            
                            count += 1

                    else:
                        salary_change = changes_by_month[month_key][0]
                        adj_date = salary_change.adjusment_date

                        # FIRST PART OF MONTH
                        date_start_old = adj_date.replace(day=1)
                        old_salary_days = payslip_class.days360(
                            date_start_old, 
                            adj_date
                        )
                        old_salary_tot = old_salary_days * (
                            salary_change.last_salary/30
                        )
                        values_b_month[month_key] = {}
                        values_b_month[month_key]['first_value'] = (
                            month_key,
                            salary_change.last_salary
                        )

                        #SECOND PART OF MONTH
                        date_end_act = adj_date.replace(day=30)
                        act_salary_days = payslip_class.days360(
                            adj_date, 
                            date_end_act
                        ) + 1
                        act_salary_tot = act_salary_days * (
                            salary_change.amount/30
                        )
                        values_b_month[month_key]['last_value'] = (
                            month_key,
                            salary_change.amount
                        )

                        tot_rule += act_salary_tot + old_salary_tot

            for month in range(fd_month, td_month):
                month_key = str(month)
                if month_key not in changes_by_month.keys():
                    past_value = ()
                    future_value = ()
                    for key in changes_by_month:
                        if month > int(key):
                            if past_value:
                                if month > past_value[0]:
                                    past_value = (
                                        month, 
                                        values_b_month[key]['last_value'][1]
                                    )
                            else:
                                past_value = (
                                    month, 
                                    values_b_month[key]['last_value'][1]
                                )
                        else:
                            if future_value:
                                if month < future_value[0]:
                                    future_value = (
                                        month, 
                                        values_b_month[key]['first_value'][1]
                                    )
                            else:
                                future_value = (
                                    month, 
                                    values_b_month[key]['first_value'][1]
                                )
                    
                    if past_value:
                        tot_rule += past_value[1]
                    elif future_value:
                        tot_rule += future_value[1]
                    else:
                        tot_rule += self.contract_id.wage

            #tot_rule = tot_rule/months_count

        # Sueldo, dias trabajados en el mes            

        #tot_rule = self.get_salary_history_avg()
        worked_days = payslip_class.days360(from_date, to_date)
        payroll_news_ids = self._get_payroll_news_ids(from_date, to_date)
        code_ids = payroll_news_ids.filtered(
            lambda line: line.payroll_news_id.salary_rule_code in codes)

        # Horas Extras + Comisiones
        sum_total = sum([line.total for line in code_ids])
        avg_ext = (sum_total/worked_days)*30

        # Subsidio de transporte
        subsidio_t = self.dict.get_line_data(
            [code],
            fixed_days=30
        )

        # avg total
        if not tot_rule:
            tot_rule = self.contract_id.wage
        else:
            tot_rule = (tot_rule/worked_days)*30

        # Current month
        result = ((tot_rule + avg_ext + subsidio_t)*worked_days)/days
        return result

    def compute_extra_legal_premium(self, days=360):
        now_year = datetime.now().year
        month_init = 1
        month_end = 12

        from_date = datetime.now().replace(
            day=1, month=month_init, year=now_year).date()
        date_to = datetime.now().replace(
            day=31, month=month_end, year=now_year).date()
        if from_date < self.contract_id.date_start:
            from_date = self.contract_id.date_start

        # Sueldo, dias trabajados en el mes
        worked_days = self.env['hr.payslip'].days360(from_date, date_to)

        avg_salary = self.contract_id.wage
        # AGREGAR AUXILIOS
        aid_ids = self.contract_id.salary_aid_ids
        avg_aid = sum([x.value for x in aid_ids])
        aid_value = avg_aid / days

        base_day = avg_salary / days
        # AGREGAR AUXILIOS
        return (base_day + aid_value) * worked_days

    def compute_legal_premium_days(self, period=1):
        now_year = datetime.now().year
        month_init = 1 if period == 1 else 7
        month_end = 7 if period == 1 else 1
        year = now_year if period == 1 else now_year + 1

        from_date = datetime.now().replace(
            day=1, month=month_init, year=now_year).date()
        to_date = datetime.now().replace(
            day=1, month=month_end, year=year).date()
        if from_date < self.contract_id.date_start:
            from_date = self.contract_id.date_start
        if to_date > self.date_to:
            to_date = self.date_to + relativedelta(days=1)
        worked_days = self.env['hr.payslip'].days360(from_date, to_date)
        return worked_days

    def compute_provisions_severance_incremental(self,
                                                 code,
                                                 codes,
                                                 from_date,
                                                 to_date,
                                                 percentage=100,
                                                 fixed_days=30):
        # Fecha inicial tomada de la nomina
        year = from_date.year if from_date.year else datetime.now().year
        start_date = datetime.now().replace(day=1, month=1, year=year).date()
        end_date = datetime.now().replace(day=1, month=2, year=year).date()

        # Trae todos los dias que tienen la nomina aprobada
        worked_days = self.get_worked_year_days('WORK100', start_date,
                                                from_date, ['done', 'verify'])

        # Trae el total del sueldo basico + aux de transporte
        # code ['BASIC', '120']
        tot_rule = self.dict.get_line_data(
            code,
            fixed_days=fixed_days
        )

        # Calculos adicionales Novedades
        if len(codes) > 0:
            payroll_news_ids = self._get_payroll_news_ids(from_date, to_date)
            code_ids = payroll_news_ids.filtered(
                lambda line: line.payroll_news_id.salary_rule_code in codes)
            # Horas Extras + Comisiones
            sum_total = sum([line.total for line in code_ids])
            tot_rule += (sum_total/30)

        tot_severance = (tot_rule*worked_days)/360
        interest = (tot_severance*worked_days*(percentage/100))/360

        if not self.get_period_month(from_date, to_date, 1):
            prev_month = from_date - relativedelta(months=1)
            res = self.sum_payslip_line('PROINT', start_date,
                                        from_date, ['done', 'verify'])
            interest -= res[0] and abs(res[0]) or 0.0

        return interest

    def compute_provisions(self, code, codes, from_date,
                           to_date=None, percentage=100,
                           fixed_days=0, ded_codes=[]):
        if to_date is None:
            to_date = fields.Date.today()

        payroll_news_ids = self._get_payroll_news_ids(from_date, to_date)
        code_ids = payroll_news_ids.filtered(
            lambda line: line.payroll_news_id.salary_rule_code in codes)

        sum_total = sum([line.total for line in code_ids])

        tot_rule = self.dict.get_line_data(
            code,
            fixed_days=fixed_days
        )

        tot_ded = self.dict.get_line_data(
            ded_codes,
            fixed_days=fixed_days
        )

        return ((tot_rule + sum_total) * (percentage/100)) + tot_ded

    def check_adjusment(self, from_date, to_date):
        payslip_month = from_date.month
        date_end = self.contract_id.date_end

        if not date_end:
            date_end = datetime.now().replace(month=12, day=31)

        date_start = date_end + relativedelta(months=-2, day=1)
        month_range = range(date_start.month, date_end.month + 1)

        return (len(self._get_contract_history(
            from_date, to_date)) > 0 and
            payslip_month not in month_range)

    def check_annual_salary_adjustments(self, from_date, to_date):
        date_end = self.contract_id.date_end

        annual_average_start_date = self.contract_id.date_start

        if annual_average_start_date.year < from_date.year:
            annual_average_start_date = datetime.now().replace(day=1, month=1)

        if not date_end:
            date_end = datetime.now().replace(day=31, month=12).date()

        count = date_end.month - 3
        if not count > 0:
            return False

        date_start = date_end + relativedelta(
            months=-2, day=1)

        annual_average_end_date = date_start + relativedelta(
            months=-1,
            day=monthrange(date_start.year, count)[1])

        return (from_date.month == date_end.month and
                len(self._get_contract_history(
                    date_start, date_end)) > 0 and
                len(self._get_contract_history(
                    annual_average_start_date, annual_average_end_date)) > 0)

    def compute_adjusment(self, from_date, to_date):
        changes_history = self._get_contract_history(
            from_date, to_date)
        sum_amount = 0
        sum_last = 0

        for change in changes_history:
            sum_amount += change.amount
            sum_last += change.last_salary

        return sum_amount - sum_last

    def calculate_closure_setting(self, code, codes, percentage=100):
        date_start = self.contract_id.date_start
        date_end = self.contract_id.date_end
        annual_salary = 0
        annual_co_he = 0
        last_histoy = False
        count = 0
        media = 0

        if date_start.year < datetime.now().year:
            date_start = datetime.now().replace(day=1, month=1).date()

        if not date_end:
            date_end = datetime.now().replace(day=31, month=12).date()

        contract_history = self._get_contract_history(
            date_start, date_end)

        for history in contract_history:
            count += 1
            number_months = (history.adjusment_date.month - date_start.month
                             if count == 1
                             else (history.adjusment_date.month -
                                   last_histoy.adjusment_date.month))

            annual_salary += history.last_salary * number_months
            last_histoy = history
            media += number_months

            if len(contract_history) == count:
                number_months = date_end.month - \
                    (history.adjusment_date.month - 1)
                annual_salary += history.amount * number_months
                media += number_months

        # Se calculan provisiones del ultimo mes

        payslip_lines = self._get_payroll_news_ids(date_start, date_end)
        code_ids = payslip_lines.filtered(
            lambda line: line.payroll_news_id.salary_rule_code in codes)

        total_comision = sum([x.total for x in code_ids])

        last_provision_month = self.compute_provisions(
            code, codes,
            date_end + relativedelta(day=1), date_end, 100) * (percentage/100)

        total_provisions = self._get_sum_provisions(
            date_start, date_end) + last_provision_month

        worked_days = self.get_worked_year_days('WORK100', date_start,
                                                date_end, ['verify', 'done'])

        return (((annual_salary / media) + (total_comision / media))
                * worked_days/360) - (total_provisions)


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _get_base_local_dict(self):
        employee = self.employee_id
        res = super()._get_base_local_dict()
        res.update({
            'provisions': MyPayslips(employee.id, self, self.env),
        })
        return res

    def sum_demo(self):
        return 1.0

    def get_worked_days_line_ids(self, code):
        return self.worked_days_line_ids.filtered(
            lambda line: line.code == code)

    def get_line_data(self, code, days=0, fixed_days=0):
        total = 0
        worked_days_dict = {line.code: line for line in
                            self.worked_days_line_ids if line.code}
        inputs_dict = {line.code: line for line in
                       self.input_line_ids if line.code}

        employee = self.employee_id
        contract = self.contract_id
        localdict = {
            **self._get_base_local_dict(),
            **{
                'categories': BrowsableObject(employee.id, {}, self.env),
                'rules': BrowsableObject(employee.id, {}, self.env),
                'payslip': Payslips(employee.id, self, self.env),
                'worked_days': WorkedDays(
                    employee.id, worked_days_dict, self.env),
                'inputs': InputLine(employee.id, inputs_dict, self.env),
                'employee': employee,
                'contract': contract
            }
        }

        rules = self.struct_id.rule_ids.filtered(
            lambda line: line.code in code)

        for rule in sorted(rules, key=lambda x: x.sequence):
            localdict.update({
                'result': None,
                'result_qty': 1.0,
                'result_rate': 100})
            if rule._satisfy_condition(localdict):
                amount, qty, rate = rule._compute_rule(localdict)
                qty = (qty - days) if days > 0 else qty
                qty = fixed_days if fixed_days > 0 else qty
                total += amount * qty * rate / 100.0
        return total

    def days360(self, start_date, end_date, method_eu=False):
        start_day = start_date.day
        start_month = start_date.month
        start_year = start_date.year
        end_day = end_date.day
        end_month = end_date.month
        end_year = end_date.year

        if (
            start_day == 31 or
            (
                method_eu is False and
                start_month == 2 and (
                    start_day == 29 or (
                        start_day == 28 and
                        start_date.is_leap_year is False
                    )
                )
            )
        ):
            start_day = 30

        if end_day == 31:
            if method_eu is False and start_day != 30:
                end_day = 1

                if end_month == 12:
                    end_year += 1
                    end_month = 1
                else:
                    end_month += 1
            else:
                end_day = 30

        return (
            end_day + end_month * 30 + end_year * 360 -
            start_day - start_month * 30 - start_year * 360)
