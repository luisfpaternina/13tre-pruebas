# -*- coding: utf-8 -*-
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _

from collections import defaultdict
from odoo.addons.hr_payroll.models.browsable_object \
    import BrowsableObject, InputLine, WorkedDays, Payslips

from odoo.addons.hr_payroll_severance_pay.models.models \
    import MyPayslips


class Indemnities(BrowsableObject):

    def _sum_enjoyed_days(self, from_date):
        self.env.cr.execute("""
            SELECT sum(re.days_taken + re.compesated_in_money) as total
            FROM hr_payroll_holiday_lapse as re
            WHERE re.employee_id = %s AND re.begin_date >= %s""", (
            self.employee_id, from_date))
        return self.env.cr.fetchone()[0] or 0.0

    def sum_enjoyed_days(self, last_years=5):
        fecha_contrato = self.dict.contract_id.date_start
        return self._sum_enjoyed_days(fecha_contrato)

    def get_total_enjoyed_holidays(self):
        # TODO traer esta informacion desde el libro de vacaciones
        return self.sum_enjoyed_days()

    def _get_payroll_news_ids(self, from_date, to_date):
        return self.env['hr.employee.payroll.news'].search(
            [('employee_id', '=', self.employee_id),
             ('payroll_news_id.date_start', '>=', from_date),
             ('payroll_news_id.date_end', '<=', to_date),
             '|',
             ('payroll_news_id.stage_id.is_approved', '=', True),
             ('payroll_news_id.stage_id.is_won', '=', True)])

    def _get_settlement(self):
        return self.env['settlement.history'].search([
            ('payslip_id', '=', self.dict.id)
        ], limit=1)

    def _sum(self, code, from_date, to_date, state=['done']):
        self.env.cr.execute("""
            SELECT (sum(pi.amount) / 30) * sum(pi.number_of_days) as total,
            sum(pi.number_of_days) as number_of_days,
            count(hp.id) as payslip_count
            FROM hr_payslip as hp, hr_payslip_worked_days as pi,
            hr_work_entry_type as wet
            WHERE hp.employee_id = %s AND hp.state IN %s
            AND hp.date_from >= %s AND hp.date_to <= %s AND
            hp.id = pi.payslip_id AND pi.work_entry_type_id = wet.id
            AND wet.code = %s GROUP BY pi.id""", (self.employee_id, 
                                                  tuple(state),
                                                  from_date, 
                                                  to_date, 
                                                  code))
        return self.env.cr.fetchall()

    def sum(self, code, from_date, to_date, state=['done']):
        return self._sum(code, from_date, to_date, state)

    def get_contract_type(self, _type):
        settlement_id = self._get_settlement()
        res = False if (not settlement_id or
                        settlement_id.type_contract != _type) else True
        return res

    def calculation_indenminazion_fixed(self):
        # Indemnización por despido sin justa causa en el
        # Contrato de trabajo a término fijo
        settlement_id = self._get_settlement()
        indemnify_months = settlement_id.missing_time or 1
        basic_wage = self.dict._get_contract_wage()
        return basic_wage * indemnify_months

    def calculation_indenminazion_non_fixed(self, init_days=30,
                                            others_days=20):
        # Indemnización por despido sin justa
        # Causa en el contrato a término indefinido
        # Inferior a 10 SMLV  - Laboro Mas de un Año
        settlement_id = self._get_settlement()
        basic_wage = self.dict._get_contract_wage()
        running_time = settlement_id.running_time or 0
        init_pay = init_days if running_time >= 12 else init_days
        others_pay = (running_time - 12)*others_days/12 \
            if running_time >= 12 else 0
        return (basic_wage/30) * (init_pay + others_pay)

    def compute_settlement_holidays_pay(self, code, codes,
                                        from_date, to_date, days=30,
                                        holidays=15):
        settlement_id = self._get_settlement()
        to_date = settlement_id.date_end or datetime.now().date()
        from_date = to_date + relativedelta(years=-1)

        tot_rule = self.dict._get_contract_wage()
        running_time = settlement_id.running_time or 0
        work_days = settlement_id.work_days or 0
        days_unpaid = settlement_id.days_unpaid or 0

        # Si los días trabajados son mayores a 360, se debe calcular sobre 360
        # para hacer el prorrateo, de lo contrario se calcula sobre los días
        # trabajados
        worked_days = 360 if work_days > 360 else work_days
        days_taken = self.get_total_enjoyed_holidays()
        total = work_days - ((days_taken*worked_days)/holidays) - days_unpaid
        if total <= 0:
            return 0
        # Traer datos del año
        # Calculos adicionales Novedades
        if len(codes) > 0:
            payroll_news_ids = self._get_payroll_news_ids(from_date, to_date)
            code_ids = payroll_news_ids.filtered(
                lambda line: line.payroll_news_id.salary_rule_id.code in codes)
            # Horas Extras + Comisiones
            sum_total = sum([line.total for line in code_ids])
            tot_rule += (sum_total/worked_days)*days
        return ((tot_rule*total)/720)

    def compute_settlement_severance_pay_interest(self, code, codes, from_date,
                                                  to_date, percentage=12,
                                                  period=3, days=360):
        from_date = datetime.now().replace(day=1, month=1).date()
        if from_date < self.contract_id.date_start:
            from_date = self.contract_id.date_start
        to_date = datetime.now().replace(day=31, month=12).date()
        settlement_id = self._get_settlement()
        days_unpaid = settlement_id.get_total_unpaid_news(
            from_date, settlement_id.date_end)
        worked_days = settlement_id.days_360(
            from_date, settlement_id.date_end) - days_unpaid
        tot_severance = self.compute_settlement_severance_pay(
            code, codes, period, days)
        return (tot_severance * worked_days * (percentage/100)) / days

    def compute_settlement_severance_pay(self, code, codes,
                                         period=3, days=360):
        settlement_id = self._get_settlement()
        from_date = datetime.now().replace(day=1, month=1).date()
        if from_date < self.contract_id.date_start:
            from_date = self.contract_id.date_start
        to_date = settlement_id.date_end or datetime.now().date()
        days_unpaid = settlement_id.get_total_unpaid_news(
            from_date, to_date)
        running_time = settlement_id.days_360(
            from_date, to_date) - days_unpaid
        tot_rule = self.dict._get_contract_wage()
        payslip_count = 1
        # subsidio de transporte
        tot_help = self.dict.get_line_data(
            ['120'],
            fixed_days=30
        )
        from_date_period = to_date - relativedelta(months=period)
        if from_date_period >= from_date:
            lines = self.dict.contract_id.contract_history_ids.filtered(
                lambda line: from_date_period >= line.date
                and line.date <= to_date)
            severance = MyPayslips(self.employee_id, self, self.env)
            res = severance.sum(code, from_date, to_date)
            tot_rule += res[0] and res[0] or 0.0
            payslip_count += res[2] and res[2] or 0.0
        # Calculos adicionales Novedades
        sum_total = 0
        if len(codes) > 0:
            payroll_news_ids = self._get_payroll_news_ids(from_date, to_date)
            code_ids = payroll_news_ids.filtered(
                lambda line: line.payroll_news_id.salary_rule_code in codes)
            # Horas Extras + Comisiones
            sub_total = sum([line.total for line in code_ids])
            sum_total += ((sub_total/running_time)*30)
        # Promedio de todos/ultimo salario por (dias trabajados / 360)
        tot_severance = (((tot_rule/payslip_count) + tot_help + sum_total)
                         * running_time) / days
        return tot_severance

    def compute_settlement_legal_premium(self, code, codes,
                                         period=1, days=360):
        now_year = datetime.now().year
        month_init = 1 if period == 1 else 7
        tot_val = 0

        from_date = datetime.now().replace(
            day=1, month=month_init, year=now_year).date()
        to_date = self.date_to

        # Sueldo, dias trabajados en el mes
        res = self.sum('WORK100', from_date, to_date)
        tot_rule = sum(r[0] for r in res) if res else 0
        worked_days = sum(r[1] for r in res) if res else 0
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
        tot_rule += ((current.amount if current.amount > 0 else 0) / 30)  \
                    * current.number_of_days
        worked_days += current.number_of_days if current.number_of_days else 0

        if worked_days:
            sum_others = sum_total + subsidio_t
            tot_rule = ((tot_rule / worked_days) * 30) + sum_others
            tot_val = (tot_rule * worked_days)/days

        return tot_val


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _get_base_local_dict(self):
        employee = self.employee_id
        res = super()._get_base_local_dict()
        res.update({
            'indemnities': Indemnities(employee.id, self, self.env),
        })
        return res

    def _get_settlement(self):
        return self.env['settlement.history'].search([
            ('payslip_id', 'in', self.ids)
        ], limit=1)

    # Commented Requirement 17020 - Task 17151 - Nomina Electronica
    """ 
    def action_payslip_done(self):
        res = super().action_payslip_done()
        for record in self:
            if record.struct_id.type_id.name == 'Liquidación':
                record.contract_id.write({
                    'date_end': record.date_to,
                    'state': 'cancel',
                })
        return res """
