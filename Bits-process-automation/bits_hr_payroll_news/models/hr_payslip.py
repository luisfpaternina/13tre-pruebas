from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from ast import literal_eval
from odoo import api, fields, models, _
from odoo.tools import float_round
from odoo.exceptions import ValidationError, UserError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    commission = fields.Float(
        strin='Commission',
        compute='_compute_commission',
        default=0
    )

    # Se comenta para mejorar el rendimiento de la generacion de las nominas
    # @api.constrains('currency_company_id')
    # def _validate_currency_company(self):
    #     for record in self:
    #         if not record.currency_company_id:
    #              raise UserError(_("Please add a currency in the company."))
    #
    # Se crea consulta sql para validacion la regla de comisiones y asignarla
    # y traerla d elas novedades.
    def get_news_by_employee(self, params):
        query_sql = (
            "SELECT  hepn.id, hepn.amount*hepn.quantity AS total "
            "FROM hr_employee_payroll_news AS hepn "
            "JOIN hr_payroll_news AS hpn ON hpn.id=hepn.payroll_news_id "
            "JOIN hr_salary_rule AS hsr ON hsr.id=hpn.salary_rule_id "
            "JOIN hr_payroll_news_stage AS hpns ON hpns.id=hpn.stage_id "
            "WHERE employee_id=%s AND hsr.code=%s "
            "AND hpn.date_start>=%s AND hpn.date_start<=%s "
            "AND hpns.is_approved=true;"
        )
        self.env.cr.execute(query_sql, params)
        result = self.env.cr.dictfetchall()
        return result

    @api.depends('line_ids')
    def _compute_commission(self):
        for record in self:
            code_commission = '321'
            params = [record.employee_id.id, code_commission,
                      record.date_from, record.date_to]
            record.commission = 0
            if record.employee_id and record.employee_id.id:
                result = record.get_news_by_employee(params)
                record.commission = sum([line['total'] for line in result])

    def add_salary_rule(self):
        list_salary_rule = []
        return list_salary_rule

    def total_const_and_non_const(self, affect_worked_days, rules):
        sum_worked_days_total = 0
        non_const_tot = 0
        const_tot = 0
        for rule in sorted(rules, key=lambda x: x['sequence']):
            if rule['code'] == 'GROSS' or rule['code'] == 'NET':
                continue

            is_constitutive = rule['is_constitutive']
            affect_payslip = rule['affect_payslip']
            del rule['is_constitutive']

            if not affect_payslip:
                if 'salary_rule_id' in rule and rule['salary_rule_id']:
                    rule_obj = self.env['hr.salary.rule'].browse(
                        rule['salary_rule_id']
                    )
                    if rule_obj.affect_const_non_const:
                        amount, qty, rate = (
                            rule['amount'], rule['quantity'], rule['rate']
                        )
                        tot_rule = amount * qty * rate / 100.0
                        if is_constitutive == 'is_const':
                            const_tot += abs(tot_rule)
                        elif is_constitutive == 'non_const':
                            non_const_tot += abs(tot_rule)
                continue

            amount, qty, rate = rule['amount'], rule['quantity'], rule['rate']
            tot_rule = amount * qty * rate / 100.0

            if is_constitutive == 'is_const':
                const_tot += abs(tot_rule)
            elif is_constitutive == 'non_const':
                non_const_tot += abs(tot_rule)

            if rule['code'] in affect_worked_days:
                sum_worked_days_total += tot_rule

        return const_tot, non_const_tot, sum_worked_days_total

    def constitutive_adjust(self, constitutive, const_tot, rules):
        for code in constitutive:
            apply_amount_per = False
            const_percentage = rules[code]['const_percentage']
            del rules[code]['const_percentage']
            # Total constituent payments apply if > (Percentage based on)
            # field hr.salary.rule -> amount_percentage_base
            # Ex: cost_total > 4*smlv
            if rules.get(code, False) and rules[code]['quantity'] == 0 and \
               const_tot > rules[code]['amount']:
                rules[code]['quantity'] = 1
                apply_amount_per = True

            if rules.get(code, False) and rules[code]['rate'] \
               and rules.get('NET', False):
                rules[code]['amount'] = const_tot * const_percentage / 100.0
                rules[code]['total'] = rules[code]['amount'] * \
                    rules[code]['rate'] / 100.0
                rules['NET']['amount'] += rules[code]['total'] \
                    if rules.get('NET', False) and apply_amount_per else 0

    def non_constitutive_adjust(self, non_constitutive, constitutive,
                                const_tot, non_const_tot,
                                sum_worked_days_total, rules,
                                non_constitutive_percentage):
        for code in non_constitutive:
            percentage = rules[code]['non_const_per']
            percentage_up = rules[code]['non_const_per_up']
            apply_salary = rules[code]['apply_salary']

            total = 0

            del rules[code]['non_const_per']
            del rules[code]['non_const_per_up']
            del rules[code]['apply_salary']

            if percentage_up > 0:
                total_up = (const_tot + non_const_tot) * percentage_up / 100.0
                if non_const_tot > total_up:
                    total += non_const_tot - total_up

            if code in constitutive and rules.get(code, False) and \
               rules[code]['amount'] > 0:
                total += rules[code]['amount']
                percentage = non_constitutive_percentage[code] \
                    if percentage == 0 else percentage

            total = (total - sum_worked_days_total) if apply_salary else total

            rules[code]['amount'] = (total * percentage / 100.0) \
                if (rules.get(code, False) and rules[code]['rate']) \
                else rules[code]['amount']
            rules[code]['total'] = rules[code]['amount'] * \
                rules[code]['rate']/100.0 \
                if (rules.get(code, False) and rules[code]['rate']) \
                else rules[code]['total']

    def net_gross_adjust(self, rules):
        gross_total = 0
        net_total = 0
        for code, rule in rules.items():
            if rule['code'] == 'GROSS' or rule['code'] == 'NET':
                continue
            affect_payslip = rule['affect_payslip']
            del rule['affect_payslip']

            if not affect_payslip:
                continue

            amount, qty, rate = rule['amount'], \
                rule['quantity'], rule['rate']

            tot_rule = self.get_total_rounding(
                rule['code'],
                amount * qty * rate / 100.0
            )

            if tot_rule > 0:
                gross_total += tot_rule
            else:
                net_total += abs(tot_rule)

        return net_total, gross_total

    # Cálculo de beneficios = No Remunerate Work days Solo se ven
    # afeactados por las reglas con No remunerado en False
    def calculation_benefit_days(self, affect_benefit_days,
                                 sum_days, res_days, rules,
                                 non_remunerate, remunerate):
        for code, benefit_type in affect_benefit_days:
            days = (sum_days + res_days) if benefit_type == 'none' else \
                (sum([abs(line) for line in non_remunerate])) \
                if benefit_type == 'non_rem_work_days' else \
                (sum([abs(line) for line in remunerate]))
            rules[code]['quantity'] -= days
            rules[code]['total'] = rules[code]['quantity'] * \
                rules[code]['rate'] / 100.0

    def calculation_affect_secu_social(self, affect_secu_social, rules,
                                       non_constitutive, constitutive,
                                       non_const_perc):
        for code, items in affect_secu_social:
            amount, qty, rate, apply_in, exclude_in = rules[code]['amount'], \
                rules[code]['quantity'], rules[code]['rate'], \
                rules[code]['apply_in'] if 'apply_in' in rules[code] else False, \
                rules[code]['exclude_in'] if 'exclude_in' in rules[code] else False

            if apply_in:
                del rules[code]['apply_in']
            if exclude_in:
                del rules[code]['exclude_in']
            tot_rule = amount * qty * rate / 100.0

            for parent in items:
                if not rules.get(parent, False):
                    continue
                percentage = non_const_perc[parent]['non_const_per'] \
                    if parent in non_constitutive \
                    else non_const_perc[parent]['const_per'] \
                    if 'const_per' in non_const_perc and \
                    non_const_perc[parent]['const_per'] else 100

                if apply_in == 'amount':
                    rules[parent]['amount'] += tot_rule * (percentage/100.0)
                    rules[parent]['total'] = rules[parent]['amount'] * \
                        rules[parent]['rate']/100.0 \
                        if (rules.get(parent, False) and
                            rules[parent]['rate']) \
                        else rules[parent]['total']
                elif apply_in == 'total':
                    if rules[code]['code'] == 'suma-ibc':
                        tot_rule = tot_rule * -1 if tot_rule > 0 else tot_rule
                    else:
                        tot_rule = abs(tot_rule)

                    rules[parent]['total'] = (rules[parent]['amount'] *
                                              rules[parent]['rate']/100.0
                                              if (rules.get(parent, False) and
                                                  rules[parent]['rate'])
                                              else rules[parent]['total']
                                              ) + tot_rule
                
                if exclude_in == 'amount':
                    rules[parent]['amount'] -= tot_rule * (percentage/100.0)
                    rules[parent]['total'] = rules[parent]['amount'] * \
                        rules[parent]['rate']/100.0 \
                        if (rules.get(parent, False) and
                            rules[parent]['rate']) \
                        else rules[parent]['total']
                elif exclude_in == 'total':
                    if rules[code]['code'] == 'suma-ibc':
                        tot_rule = tot_rule * -1 if tot_rule > 0 else tot_rule
                    else:
                        tot_rule = abs(tot_rule)

                    rules[parent]['total'] = (rules[parent]['amount'] *
                                              rules[parent]['rate']/100.0
                                              if (rules.get(parent, False) and
                                              rules[parent]['rate'])
                                              else rules[parent]['total']
                                              ) - tot_rule

    def format_rules(self, rules):
        sum_days = 0
        res_days = 0
        constitutive = list()
        non_constitutive = list()
        affect_worked_days = list()
        affect_benefit_days = list()
        non_remunerate = list()
        remunerate = list()
        affect_benefit_days = list()
        affect_secu_social = list()
        non_const_perc = dict()
        for rule in sorted(rules, key=lambda x: x['sequence']):
            if rule['code'] == 'GROSS' or rule['code'] == 'NET':
                continue

            qty = rule['quantity']
            record = self.env['hr.salary.rule'].browse(rule['salary_rule_id'])
            _data = dict()

            if record.affect_worked_days:
                affect_worked_days.append(record.code)
                days = qty * record.affect_percentage_days
                if record.not_remunerate:
                    non_remunerate.append(days)
                else:
                    remunerate.append(days)
                if days > 0:
                    sum_days += abs(days)
                else:
                    res_days += abs(days)

            rule['affect_payslip'] = record.affect_payslip
            rule['is_constitutive'] = record.constitutive

            if record.non_constitutive_calculate:
                rule['non_const_per'] = record.non_constitutive_percentage
                rule['non_const_per_up'] = record.non_const_percentage_up
                rule['apply_salary'] = record.apply_only_basic_salary
                non_constitutive.append(record.code)
                _data.update({
                    'non_const_per': record.non_constitutive_percentage})
            if record.benefit_calculate:
                affect_benefit_days.append(
                    (record.code, record.benefit_calculate)
                )

            if record.constitutive_calculate:
                constitutive.append(record.code)
                rule['const_percentage'] = record.constitutive_percentage
                _data.update({'const_per': record.constitutive_percentage})

            non_const_perc.update({record.code: _data})

            if record.apply_other_rules:
                rule['apply_in'] = record.apply_in
                affect_secu_social.append((
                    record.code, record.apply_other_rules.split(",")))
            
            if record.exclude_other_rules:
                rule['exclude_in'] = record.exclude_in
                affect_secu_social.append(
                    (
                        record.code, 
                        record.exclude_other_rules.split(",")
                    )
                )

        return sum_days, res_days, constitutive, non_constitutive,\
            affect_worked_days, affect_benefit_days, affect_secu_social,\
            non_const_perc, non_remunerate, remunerate

    def _validate_rules_rate(self, dict_rules):
        rate_rules_dict = dict(
            ARL=self.contract_id.rate
        )

        for line in [x for x in dict_rules
                     if x['code'] in rate_rules_dict.keys()]:
            line['rate'] = rate_rules_dict.get(line['code'])

    def _get_calculate_payslip_lines(self, values):
        rules = list(values)
        self._validate_rules_rate(rules)

        integrate_payroll_news = self.env['ir.config_parameter'].sudo()\
            .get_param('hr_payroll.integrate_payroll_news')

        if integrate_payroll_news:
            rules += self.add_salary_rule()

        sum_days, res_days, constitutive, \
            non_constitutive, affect_worked_days,\
            affect_benefit_days, affect_secu_social,\
            non_const_perc, non_remunerate,\
            remunerate = self.format_rules(rules)

        res = dict((value['code'], value) for value in rules)

        self.calculation_benefit_days(
            affect_benefit_days,
            sum_days,
            res_days,
            res,
            non_remunerate,
            remunerate
        )

        const_tot, non_const_tot, sum_worked_days_total = self.\
            total_const_and_non_const(affect_worked_days, rules)
        self.constitutive_adjust(constitutive, const_tot, res)
        self.non_constitutive_adjust(
            non_constitutive,
            constitutive,
            const_tot,
            non_const_tot,
            sum_worked_days_total,
            res,
            non_const_perc
        )
        if res.get('ICO', False) and const_tot >= 0:
            res['ICO']['quantity'] = 1
            res['ICO']['amount'] = const_tot

        if res.get('INCO', False) and non_const_tot >= 0:
            res['INCO']['quantity'] = 1
            res['INCO']['amount'] = non_const_tot

        self.calculation_affect_secu_social(
            affect_secu_social,
            res,
            non_constitutive,
            constitutive,
            non_const_perc
        )
        net_total, gross_total = self.net_gross_adjust(res)
        if res.get('GROSS', False) and gross_total >= 0:
            res['GROSS']['amount'] = gross_total

        if res.get('NET', False) and gross_total >= 0:
            res['NET']['amount'] = gross_total - net_total

        self.validate_contract_change(res)

        return res

    def _get_payslip_lines(self):
        self.ensure_one()
        values = super(HrPayslip, self)._get_payslip_lines()
        return self._get_calculate_payslip_lines(values).values()

    def get_rounding_rule(self, total, _name='Payroll'):
        return self.env['decimal.precision'].get_rounding(_name, total)

    def get_total_rounding(self, code, total):
        str_ids = self.env['ir.config_parameter'].sudo()\
            .get_param('many2many.rounding_rule_ids')
        rules = self.env['hr.salary.rule'].browse(
            literal_eval(str_ids)).mapped('code') if str_ids else []
        if len(rules) > 0 and code in rules:
            return self.get_rounding_rule(total)
        return total

    def validate_contract_change(self, res):
        old_contract = self.env["hr.contract"].search([
            ("employee_id", "=", self.employee_id.id),
            ("date_end", ">=", self.date_from),
            ("date_end", "<=", self.date_to),
            ("state", "!=", "draft")
        ])

        structure = self.env.ref(
            "bits_hr_payroll_news.hr_payroll_structure_type_employee_04"
        )
        if len(old_contract) > 0 and self.contract_id.structure_type_id.id ==\
                structure.id:
            search = ["ARL", "SALU"]
            basic_salary = self.contract_id.company_id.basic_salary
            for row in search:
                if res.get(row, False):
                    res[row]["amount"] = basic_salary

        return res

    def get_worked_days_half_year(self, to_date, employee, days_type):
        
        if days_type == "half_year_1":
            from_date = date(to_date.year, 1, 1)
        elif days_type == "half_year_2":
            from_date = date(to_date.year, 7, 1)
        
        normal_payslips_structure = self.env.ref(
            'bits_hr_payroll_news.hr_payroll_structure_employee_01'
        )
        
        tot_days = self.days360(from_date, to_date)

        return tot_days
    
    def get_aid_value(self, contract):
        total_aid = 0

        for aid_line in contract.salary_aid_ids:
            total_aid += aid_line.value
        
        return total_aid

    def get_premium_bonus(self, to_date, employee, contract, days_type):
        worked_days = self.get_worked_days_half_year(
            to_date, 
            employee, 
            days_type
        )
        aid_value = self.get_aid_value(contract)

        bonus_value = (aid_value/360)*worked_days

        return bonus_value

    def get_premium_value_fix(self, payslip, provisions):
        
        premium_struct = self.env.ref(
                'bits_hr_payroll_news.hr_payroll_structure_premium_02'
            )

        normal_value = provisions.compute_legal_premium(
            '120',
            codes=['60','65','70','75','321'],
            period=2
        )

        if payslip.date_to.month == 12:
            from_date = date(payslip.date_to.year, 12, 1)
        elif payslip.date_to.month == 1:
            from_date = date(payslip.date_to.year, 1, 1)

        premium_payslip = self.env['hr.payslip'].search([
            ('date_from', '>=', from_date),
            ('date_to', '<=', payslip.date_to),
            ('employee_id', '=', payslip.employee_id),
            ('struct_id', '=', premium_struct.id),
        ])

        premium_value = 0
        for premium_line in premium_payslip.line_ids:
            if premium_line.code == 'BASIC':
                premium_value = premium_line.total

        if round(premium_value) != round(normal_value):
            return normal_value - premium_value
        else:
            return 0


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    affect_payslip = fields.Boolean(
        related='salary_rule_id.affect_payslip',
        readonly=True,
        store=True
    )

    def get_rounding_rule(self, total, _name='Payroll'):
        return self.env['decimal.precision'].get_rounding(_name, total)
    # se realiza sql para eliminar la regla salarial de de subsidio de
    # conectividad para mayor eficiencia

    def remove_benefit_assistance(self):
        for line in self:
            if (line.salary_rule_id.l10n_type_rule ==
                    'n_benefit_assistance' and line.total == 0.0):
                query_sql = "DELETE FROM hr_payslip_line WHERE id= %s"
                params = [line.id]
                line.env.cr.execute(query_sql, params)

    @api.depends('quantity', 'amount', 'rate')
    def _compute_total(self):
        super(HrPayslipLine, self)._compute_total()
        self.remove_benefit_assistance()
        str_ids = self.env['ir.config_parameter'].sudo()\
            .get_param('many2many.rounding_rule_ids')
        rules = self.env['hr.salary.rule'].browse(
            literal_eval(str_ids)).mapped('code') if str_ids else []
        for line in self:
            if len(rules) > 0 and line.code in rules:
                line.total = self.get_rounding_rule(line.total)

            if line.salary_rule_id.l10n_type_rule == 'connectivity_rule':
                obj_rule = self.env['hr.salary.rule'].search(
                    [('l10n_type_rule', '=', 'connectivity_rule')])
                amount_fix = obj_rule[0].amount_fix
                line.total = int(round(30*amount_fix, 3))
