from odoo import api, fields, models, _
from datetime import date
from ast import literal_eval
import calendar
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.addons.hr_payroll.models.browsable_object \
    import BrowsableObject, InputLine, WorkedDays, Payslips


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    # overwrite method in hr_payroll_approval
    def approve_payroll(self):
        result = super(HrPayslip, self).approve_payroll()
        for record in self:
            record.holiday_settlement()
        return result

    # IBC PAYROLL HOLIDAYS VARIATIONS
    def get_old_ibc_calc(self):
        # Obtener nómina mes anterior
        init_date, end_date = self.get_previous_range_period()
        payslips_old = self.env["hr.payslip"].search([
            ("employee_id", "=", self.employee_id.id),
            ("date_from", ">=", init_date),
            ("date_to", "<=", end_date),
            ("state","=","done"),
        ])

        # Obtener totales de ingresos constitutivos y no constutivos
        inco_total = sum([x.amount for x in payslips_old.line_ids.filtered(
            lambda line: line.code == 'INCO')])
        ico_total = sum([x.amount for x in payslips_old.line_ids.filtered(
            lambda line: line.code == 'ICO')])

        # Calcular total IBC
        total_income = inco_total + ico_total
        percentage_income = total_income * 0.4
        excess = inco_total - percentage_income
        total = ico_total + excess if excess > 0 else ico_total

        return total

    def get_previous_range_period(self):
        previous_date = self.monthdelta(self.date_to, -1)
        init_date = date(previous_date.year, previous_date.month, 1)
        end_date_day = calendar.monthrange(
            previous_date.year, previous_date.month)[1]
        end_date = date(previous_date.year, previous_date.month, end_date_day)
        return init_date, end_date

    def monthdelta(self, date, delta):
        m, y = (
            date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
        m = 12 if not m else m
        d = min(date.day, calendar.monthrange(y, m)[1])
        return date.replace(day=d, month=m, year=y)

    def validate_vacation(self):
        # Obtener datos de vacaciones
        holidays = self.env["hr.payroll.holidays.history"].search([
            ("employee", "=", self.employee_id.id),
            ("enjoyment_start_date", ">=", self.date_from),
            ("enjoyment_end_date", "<=", self.date_to),
            ("global_state", "=", "approval")
        ])

        # Obtener días de vacaciones
        holidays_quanity = 0
        for holiday in holidays:
            holidays_quanity += holiday.holidays
            holidays_quanity += holiday.enjoyment_current_month

        return True if holidays else False, holidays_quanity

    def _get_calculate_payslip_lines(self, values):
        rules = super(HrPayslip, self)._get_calculate_payslip_lines(values)
        rules = self.calc_ibc_adjust(rules)
        return rules

    def affect_other_rules(self, rules, rule, affect_codes, apply_in):
        amount, qty, rate = rule['amount'], \
            rule['quantity'], rule['rate']

        tot_rule = amount * qty * rate / 100.0

        for parent in affect_codes:
            if not rules.get(parent, False):
                continue
            percentage = rules[parent]["rate"]
            percentage = percentage if percentage else 100

            if apply_in == 'amount':
                rules[parent]['amount'] += tot_rule
                rules[parent]['total'] = rules[parent]['amount'] * \
                    rules[parent]['rate']/100.0 \
                    if (rules.get(parent, False) and
                        rules[parent]['rate']) \
                    else rules[parent]['total']

            elif apply_in == 'total':
                tot_rule = abs(tot_rule)

                rules[parent]['total'] = (rules[parent]['amount'] *
                                          rules[parent]['rate']/100.0
                                          if (rules.get(parent, False) and
                                          rules[parent]['rate'])
                                          else rules[parent]['total']
                                          ) + tot_rule
        return rules

    def calc_ibc_adjust(self, rules):
        # Validar vacaciones
        validator, holidays_quanity = self.validate_vacation()

        if validator:
            ico_total = 0
            inco_total = 0
            total = 0
            for code, rule in rules.items():
                # Obtener información de ingresos constitutivos y no
                # constitutivos
                if code == "ICO":
                    ico_total = rule.get('amount', 0)
                elif code == "INCO":
                    inco_total = rule.get('amount', 0)
                elif code == "IBC":

                    # Realizar cálculo de diferencia prorrateada
                    old_ibc = self.get_old_ibc_calc()
                    rules[code]["amount"] = (old_ibc-ico_total) /\
                        30 * holidays_quanity if old_ibc > ico_total else 0

                    # Aplicar cambios a otras reglas
                    salary_rule = self.env["hr.salary.rule"].search([
                        ("code", "=", code),
                        ("struct_id", "=", self.struct_id.id)
                    ])
                    apply_other_rules = salary_rule.apply_other_rules
                    affect_codes = salary_rule.apply_other_rules
                    affect_codes = affect_codes.split(",") if affect_codes\
                        else ""
                    apply_in = salary_rule.apply_in
                    if apply_other_rules:
                        rules = self.affect_other_rules(
                            rules, rule, affect_codes, apply_in)

        return rules
    # IBC PAYROLL HOLIDAYS VARIATIONS

    def _find_holiday_structure(self):
        return self.env.ref(
            'hr_payroll_holidays_history.structure_holidays')

    def _find_salary_rule(self, code):
        return self.env['hr.salary.rule'].search([
            ('code', '=', code)
        ], limit=1)

    def holiday_settlement(self):
        code_rules = [('145', '146'), ('148', '148-1')]
        holidays_structure = self._find_holiday_structure()

        if not self.struct_id.id == holidays_structure.id:
            return

        salary_rule = self._find_salary_rule('150')
        quantity = 0

        for codes in code_rules:
            holiday_novelties = [x.payroll_news_id for x in
                                 self.line_ids.filtered(
                                     lambda line: line.code
                                     in codes and line.payroll_news_id)]

            if holiday_novelties:
                for h_novelty in holiday_novelties:
                    quantity += sum([x.quantity for x
                                    in [n.employee_payroll_news_ids
                                        for n in h_novelty]])

                novelty = \
                    [n for n in
                        [h_novelty for h_novelty in holiday_novelties]][0][0]

                new_novelty = self.env['hr.payroll.news'].create(
                    dict(
                        name=_('Holidays settlement'),
                        request_date_from=novelty.request_date_from,
                        request_date_to=novelty.request_date_to,
                        date_start=novelty.date_start,
                        date_end=novelty.date_end,
                        payroll_structure_id=novelty
                        .payroll_structure_id.id,
                        salary_rule_id=salary_rule.id,
                        employee_payroll_news_ids=[(0, 0, {
                            'employee_id': self.employee_id.id,
                            'amount': 0,
                            'quantity': quantity
                        })]))

                for employee_payroll in new_novelty.employee_payroll_news_ids:
                    employee_payroll.write({
                        'quantity': quantity
                    })

    # overwrite function at bits_hr_payroll_news_related, search_payroll_news
    def get_holidays_structure_rules(self):
        cod_rules = []
        str_structs_ids = self.env['ir.config_parameter'].sudo()\
            .get_param('many2many.holiday_structure_ids')

        if not str_structs_ids:
            return False

        structures = self.env['hr.payroll.structure'].search([
            ('id', 'in', literal_eval(str_structs_ids))
        ])

        for structure in structures:
            cod_rules += [x.code for x in structure.rule_ids]

        return cod_rules

    def search_payroll_news(self):
        result = super(HrPayslip, self).search_payroll_news()
        holiday_structure = self._find_holiday_structure()

        rules_allowed = self.get_holidays_structure_rules()
        if self.struct_id.id == holiday_structure.id \
                and rules_allowed:
            result = result.filtered(
                lambda x: x.payroll_news_id.salary_rule_id.code
                in rules_allowed)

        return result
