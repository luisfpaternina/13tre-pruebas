# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_compare, float_is_zero
import time


class HrPayrollAccountPartner(models.Model):
    _inherit = ['hr.payslip']

    def _validate_analytic_account_account(self, salary_rule):
        has_account_analytic = True
        for accounting in salary_rule.salary_rule_account_ids:
            if not accounting.account_analytic_id:
                has_account_analytic = True
        return has_account_analytic

    def _validate_social_social_security(self, salary_rule):
        has_social_security = False
        for accounting in salary_rule.salary_rule_account_ids:
            if not accounting.social_security_id:
                has_social_security = True
        return has_social_security

    def get_data_payslip(self):
        slip_mapped_data = {
            slip.struct_id.journal_id.id: {fields.Date().end_of(
                slip.date_to, 'month'): self.env['hr.payslip']}
            for slip in self}
        for slip in self:
            slip_mapped_data[
                slip.struct_id.journal_id.id][fields.Date().end_of(
                    slip.date_to, 'month')] |= slip
        return slip_mapped_data

    def _get_account_debit_move(self, salary_rule, entity_social_security_id):
        debit_account = next((
            accounting.account_account_id for accounting
            in salary_rule.salary_rule_account_ids
            if (accounting.social_security_id.id ==
                entity_social_security_id
                and accounting.account_type == "debit")), False)
        return debit_account

    def _get_account_credit_move(self, salary_rule, entity_social_security_id):
        credit_account = next((
            accounting.account_account_id for accounting
            in salary_rule.salary_rule_account_ids
            if (accounting.social_security_id.id ==
                entity_social_security_id
                and accounting.account_type == "credit")), False)
        return credit_account

    def get_account_parafiscal(self, salary_rule, social_security_ids):
        debit_account = False
        credit_account = False
        for entity_social in social_security_ids:
            debit_account = self._get_account_debit_move(
                salary_rule, entity_social.id)

            credit_account = self._get_account_credit_move(
                salary_rule, entity_social.id)
            if ((debit_account and credit_account) or
                    (debit_account or credit_account)):
                break
        return debit_account, credit_account

    def get_account_cost_center(self, salary_rule, center_cost):
        debit_account = False
        credit_account = False
        salary_rule_account_ids = (
            salary_rule.salary_rule_account_ids
            if salary_rule.salary_rule_account_ids else [])
        for rule_account in salary_rule_account_ids:
            account = rule_account.account_account_id
            if (rule_account.account_analytic_id.id ==
                    center_cost.account_analytic_id.id):
                debit_account = (
                    account if rule_account.account_type == 'debit' else False)
                credit_account = (
                    account if rule_account.account_type == 'credit'
                    else False)
        return credit_account, debit_account

    def default_account_account(self, salary_rule, account_ype):
        account = False
        for accounting in salary_rule.salary_rule_account_ids:
            if (accounting.account_type == account_ype
                    and not accounting.social_security_id
                    and not accounting.account_analytic_id):
                account = accounting.account_account_id
                break
        return account

    def _get_entities_parafiscal(self, employee_id):
        social_security_ids = self.env['social.security']
        social_security_ids += employee_id.arl
        social_security_ids += employee_id.health
        social_security_ids += employee_id.pension
        social_security_ids += employee_id.layoffs
        social_security_ids += employee_id.compensation_box
        return social_security_ids

    def validate_account_line(self, salary_rule, center_cost=False,
                              social_security_ids=[], request=None):
        debit_account = False
        credit_account = False
        if salary_rule.search_parafiscales and request == 'pf':
            return self.get_account_parafiscal(salary_rule,
                                               social_security_ids)
        if salary_rule.applies_all_cost_center and request == 'cc':
            return self.get_account_cost_center(salary_rule, center_cost)

        if center_cost:
            debit_account = next((
                accounting.account_account_id for accounting
                in salary_rule.salary_rule_account_ids
                if (accounting.account_analytic_id.id ==
                    center_cost.account_analytic_id.id
                    and accounting.account_type == "debit")),
                False)

            credit_account = next((
                accounting.account_account_id for accounting
                in salary_rule.salary_rule_account_ids
                if (accounting.account_analytic_id.id ==
                    center_cost.account_analytic_id.id
                    and accounting.account_type == "credit")),
                False)
        return debit_account, credit_account

    def _validate_value_lines(self, debit_account, credit_account,
                              paylip_line):
        debit_value = 0.0
        credit_value = 0.0
        if debit_account:
            debit_value = (paylip_line.total if paylip_line.total > 0.0
                           else 0.0)
            credit_value = (-paylip_line.total if paylip_line.total < 0.0
                            else 0.0)
        if credit_account:
            debit_value = (-paylip_line.total if paylip_line.total < 0.0
                           else 0.0)
            credit_value = (paylip_line.total if paylip_line.total > 0.0
                            else 0.0)
        if credit_account and paylip_line.total < 0.0:
            credit_value = (-paylip_line.total if paylip_line.total < 0.0
                            else 0.0)
            debit_value = 0.0
        return debit_value, credit_value

    def _get_type_account_division(self):
        type_account = {
            'equity': self.env.company.account_type_equity,
            'asset': self.env.company.account_type_asset,
            'liability': self.env.company.account_type_liability,
            'income': self.env.company.account_type_income,
            'expense': self.env.company.account_type_expense,
            'off_balance': (
                self.env.company.account_type_off_balance)
        }
        return type_account

    @api.model
    def _validate_division_center_cost(self, debit_account, credit_account):
        apply_division = False
        slip_account = debit_account if debit_account else credit_account
        type_account = self._get_type_account_division()
        if slip_account:
            account_group = slip_account.internal_group
            if type_account.get(account_group, False):
                apply_division = True
        return apply_division

    @api.model
    def _lines_center_cost(self, center_cost, debit_account,
                           paylip_line, move, partner, date, journal_id,
                           credit_account):
        line_ids = []
        debit_value = 0.0
        credit_value = 0.0
        if debit_account:
            debit_value, credit_value = (
                self._validate_value_lines(
                    debit_account, False,
                    paylip_line))
            debit_value = (
                debit_value * center_cost.percentage) / 100
            line = self._get_dict_lines(
                paylip_line.name, move.id, partner.id,
                debit_account, journal_id,
                date, debit_value, credit_value,
                center_cost.account_analytic_id.id)
            line_ids.append(line)
        if credit_account:
            debit_value, credit_value = (
                self._validate_value_lines(
                    False, credit_account,
                    paylip_line))
            credit_value = (
                credit_value * center_cost.percentage) / 100
            line = self._get_dict_lines(
                paylip_line.name, move.id, partner.id,
                credit_account, journal_id,
                date, debit_value, credit_value,
                center_cost.account_analytic_id.id)
            line_ids.append(line)
        return line_ids

    @api.model
    def _line_center_cost_pf(self, employee_center_costs, debit_account,
                             paylip_line, move, partner, date, journal_id,
                             credit_account):
        line_ids = []
        for center_cost in employee_center_costs:
            line_ids += self._lines_center_cost(
                center_cost, debit_account,
                paylip_line, move, partner, date, journal_id,
                credit_account)
        return line_ids

    @api.model
    def _line_standard_move(self, debit_account, paylip_line, move, partner,
                            date, journal_id, credit_account):
        line_ids = []
        if debit_account:
            debit_value, credit_value = (
                self._validate_value_lines(
                    debit_account, False,
                    paylip_line))
            line = self._get_dict_lines(
                paylip_line.name, move.id, partner.id,
                debit_account, journal_id,
                date, debit_value, credit_value,
                False)
            line_ids.append(line)
        if credit_account:
            debit_value, credit_value = (
                self._validate_value_lines(
                    False, credit_account,
                    paylip_line))
            line = self._get_dict_lines(
                paylip_line.name, move.id, partner.id,
                credit_account, journal_id,
                date, debit_value, credit_value,
                False)
            line_ids.append(line)
        return line_ids

    def generate_line_parafiscal(self, salary_rule, paylip_line, move,
                                 slip, partner, date, social_security_ids,
                                 employee_center_costs):
        line_ids = []
        social_security_ids = (social_security_ids if social_security_ids
                               else [])
        if salary_rule.search_parafiscales:
            debit_account, credit_account = self.validate_account_line(
                salary_rule, False, social_security_ids, 'pf')
            line_ids += self.genererate_line_NET(debit_account, credit_account,
                                                 employee_center_costs,
                                                 paylip_line, move,
                                                 partner, date, slip)
        return line_ids

    # generate line by center cost
    def generate_line_center_cost(self, employee_center_costs, salary_rule,
                                  paylip_line, date, move_id, partner, move,
                                  slip):
        line_ids = []
        journal_id = slip.struct_id.journal_id.id
        center_cost_division = False
        for center_cost in employee_center_costs:
            debit_account = []
            credit_account = []
            if (salary_rule.search_parafiscales
                    and not salary_rule.applies_all_cost_center):
                continue
            credit_account, debit_account = self.validate_account_line(
                salary_rule, center_cost, [], 'cc')
            if self._validate_division_center_cost(debit_account,
                                                   credit_account):
                lines = self._lines_center_cost(
                    center_cost, debit_account, paylip_line, move,
                    partner, date, journal_id, credit_account)
                center_cost_division = True
                line_ids += lines
        if not center_cost_division:
            line_ids += self._line_standard_move(
                debit_account, paylip_line, move, partner, date, journal_id,
                credit_account)
        return line_ids

    # Create dict line for Journal Entry
    def _get_dict_lines(self, line_name, move_id, partner_id, account,
                        journal_id, date, debit_value, credit_value,
                        account_analytic_id):
        line = {
            'name': line_name,
            'move_id': move_id,
            'partner_id': partner_id,
            'account_id': account.id,
            'journal_id': journal_id,
            'date': date,
            'debit': debit_value,
            'credit': credit_value,
            'analytic_account_id': account_analytic_id or False
        }
        return line

    def _validate_rules_for_pr(self, salary_rule, paylip_line):
        status_rule = False
        if (not salary_rule.search_parafiscales and
            not salary_rule.applies_all_cost_center and
                not paylip_line.code == 'NET'):
            status_rule = True

        if (salary_rule.search_parafiscales and
            not salary_rule.applies_all_cost_center and
                not paylip_line.code == 'NET'
                and self._validate_social_social_security(salary_rule)):
            status_rule = True

        if (not salary_rule.search_parafiscales and
            salary_rule.applies_all_cost_center and
                not paylip_line.code == 'NET'
                and self._validate_analytic_account_account(salary_rule)):
            status_rule = True
        return status_rule

        # Lines without center cost and parafiscal
    def _lines_without_ccp(self, salary_rule, paylip_line, move, slip, partner,
                           date, employee_center_costs):
        line_ids = []
        if (self._validate_rules_for_pr(salary_rule, paylip_line)):
            credit_account = self.default_account_account(
                salary_rule, 'credit')
            debit_account = self.default_account_account(
                salary_rule, 'debit')
            line_ids += self.genererate_line_NET(debit_account, credit_account,
                                                 employee_center_costs,
                                                 paylip_line, move,
                                                 partner, date, slip)
        return line_ids

    def _create_move(self, date, journal_id):
        move_dict = {
            'narration': '',
            'ref': date.strftime('%B %Y'),
            'journal_id': journal_id,
            'date': date
        }
        return move_dict

    def _validate_account_account_journal(self, account, slip):
        if not account:
            raise UserError(
                _('The Expense Journal "%s" has not properly configured '
                  'the Credit Account!') % (slip.journal_id.name))

    def get_line_adjustment_entry(self, credit_sum, debit_sum, precision,
                                  slip, move_id, partner_id, date, line_ids):
        credit = 0.0
        debit = 0.0
        acc_id = False
        account_analytic = (
            self.company_id.adjusment_entry_account_analytic.id
            if self.company_id.adjusment_entry_account_analytic else False)
        if (float_compare(
                credit_sum, debit_sum, precision_digits=precision) == -1):
            credit = abs(credit_sum - debit_sum)
            acc_id = slip.journal_id.default_credit_account_id
            self._validate_account_account_journal(acc_id, slip)
        if (float_compare(
                debit_sum, credit_sum, precision_digits=precision) == -1):
            debit = abs(credit_sum - debit_sum)
            acc_id = slip.journal_id.default_debit_account_id
            self._validate_account_account_journal(acc_id, slip)
        if not acc_id:
            return line_ids
        line = self._get_dict_lines(_("Adjusment entry"), move_id,
                                    partner_id.id, acc_id,
                                    slip.struct_id.journal_id.id,
                                    date, debit, credit, account_analytic)
        line_ids.append(line)
        return line_ids

    def genererate_line_NET(self, debit_account, credit_account,
                            employee_center_costs, paylip_line, move,
                            partner, date, slip):
        line_ids = []
        journal_id = slip.struct_id.journal_id.id
        if self._validate_division_center_cost(debit_account, credit_account):
            line_ids += self._line_center_cost_pf(
                employee_center_costs, debit_account,
                paylip_line, move, partner, date, journal_id, credit_account)
            return line_ids
        line_ids += self._line_standard_move(
            debit_account, paylip_line, move, partner, date, journal_id,
            credit_account)
        return line_ids

    # the param self is a hr.payslip
    # Cuando los valores sen negativo y tengan cuentas al credito el valor en
    # su posicion se debe inventir, es decir el credito al debito y debito al
    # credito
    def action_payslip_done(self):
        res = super(HrPayrollAccountPartner, self).action_payslip_done()
        # Se obtiene precision decimal
        precision = self.env['decimal.precision'].precision_get('Payroll')
        slip_mapped_data = self.get_data_payslip()

        for journal_id in slip_mapped_data:  # For each journal_id
            for slip_date in slip_mapped_data[journal_id]:  # For each month.
                date = slip_date
                for slip in slip_mapped_data[journal_id][slip_date]:
                    line_ids = []
                    debit_sum = 0.0
                    credit_sum = 0.0
                    move_dict = self._create_move(slip_date, journal_id)
                    social_security_ids = self._get_entities_parafiscal(
                        slip.employee_id)
                    partner = slip.employee_id.address_home_id

                    employee_center_costs = (slip.employee_id
                                             .employee_center_cost_ids)

                    # it's validated if the employee
                    # has an assigned res_partner
                    if not slip.employee_id.address_home_id:
                        raise ValidationError(
                            _('The employee must be assigned a contact'))

                    # it's validated if the employee
                    # has an assigned account analityc
                    if not slip.employee_id.employee_center_cost_ids:
                        raise ValidationError(
                            _('The employee must be assigned a center cost'))

                    move_dict['narration'] += slip.number or '' + \
                        ' - ' + slip.employee_id.name or ''
                    move_dict['narration'] += '\n'
                    move = self.env['account.move'].create(move_dict)
                    # Se recorren las lineas del calculo de la nomina
                    for paylip_line in slip.line_ids:
                        if float_is_zero(
                                paylip_line.amount,
                                precision_digits=precision):
                            continue

                        salary_rule = paylip_line.salary_rule_id

                        # Se agrega linea de net salary
                        if paylip_line.code == 'NET':
                            debit_account, credit_account = (
                                slip.validate_account_line(
                                    salary_rule, False, False, None))

                            credit_account = (slip.default_account_account(
                                salary_rule, 'credit') if not debit_account
                                and not credit_account else credit_account)

                            net_account = (debit_account
                                           if debit_account else
                                           credit_account)

                            if net_account:
                                line_ids += self.genererate_line_NET(
                                    debit_account, credit_account,
                                    employee_center_costs, paylip_line,
                                    move, partner, date, slip)

                                # FIN Asignaciones temporales
                                # Generate lines by center cost
                        line_ids += slip.generate_line_center_cost(
                            employee_center_costs, salary_rule, paylip_line,
                            date, move, partner, move, slip)
                        # Lines without center cost and parafiscal
                        line_ids += slip._lines_without_ccp(
                            salary_rule, paylip_line, move,
                            slip, partner, date, employee_center_costs)
                        # Lines with Parafiscal
                        line_ids += slip.generate_line_parafiscal(
                            salary_rule,
                            paylip_line, move,
                            slip, partner,
                            date, social_security_ids, employee_center_costs)

                    for line_id in line_ids:
                        debit_sum += line_id['debit']
                        credit_sum += line_id['credit']
                    line_ids = self.get_line_adjustment_entry(
                        credit_sum, debit_sum, precision, slip, move.id,
                        partner, date, line_ids)

                    self.env['account.move.line'].create(line_ids)
                    slip.write({'move_id': move.id})

        return res
