# -*- coding: utf-8 -*-
import json
from odoo import models, fields, api, _

class AccountDifferenceNiifColgap(models.AbstractModel):
    _name = "account.difference.niif.colgap"
    _description = "Account Difference NIIf-Colgap"
    _inherit = "account.report"

    filter_date = {'mode': 'range', 'filter': 'this_month'}
    filter_multi_company = True
    filter_all_entries = False
    filter_journals = True
    filter_analytic = False
    filter_unfold_all = False
    filter_cash_basis = None
    filter_hierarchy = False
    filter_range_account = True
    MAX_LINES = None

    @api.model
    def _init_filter_range_account(self, options, previous_options=None):
        if self.filter_range_account is None:
            return
        # Account_accounts
        model_account = "account.account"
        options['range_account'] = self.filter_range_account
        options['account_accounts'] = (
            previous_options and previous_options.get(
                'account_accounts') or [])
        account_accounts_ids = options['account_accounts']
        selected_account_accounts = (
            account_accounts_ids
            and self.env[model_account
                         ].browse(account_accounts_ids)
            or self.env[model_account])
        options['selected_account_account_names'] = (
            selected_account_accounts.mapped('name'))
        # Account_accounts_to
        options['account_accounts_to'] = (
            previous_options and previous_options.get(
                'account_accounts_to') or [])
        account_to_ids = options['account_accounts_to']
        selected_account_accounts_to = (
            account_to_ids
            and self.env[model_account
                         ].browse(account_to_ids)
            or self.env[model_account])
        options['selected_account_account_names_to'] = (
            selected_account_accounts_to.mapped('name'))

    @api.model
    def _get_columns_name(self, options):
        columns = [
            {'name': '', 'style': 'width:40%'},
            {'name': _('Balance Colgap'), 'class': 'number'},
            {'name': _('Balance NIIF'), 'class': 'number'},
            {'name': _('Difference'), 'class': 'number'}
        ]
        return columns

    @api.model
    def _get_sql_select(self, options):
        sql_select = (
            "SELECT aml.id AS aml_id, aml.name AS aml_name, "
            "aml.balance AS BALANCE, aa.id AS aa_id, aa.code AS aa_code, "
            "aa.name AS aa_name, aj.id AS aj_id, aj.name AS aj_name, "
            "aj.type AS aj_type, aj.accounting AS accounting"
        )
        return sql_select

    @api.model
    def _get_sql_from(self, options):
        sql_from = (
            " FROM account_move_line as aml "
            "INNER JOIN account_account as aa ON aa.id=aml.account_id "
            "INNER JOIN account_journal as aj ON aj.id=aml.journal_id "
        )
        return sql_from

    @api.model
    def _get_journal_move(self, options):
        journal_ids = []
        journals = options.get('journals', [])
        for journal in journals:
            if journal.get('selected', False):
                journal_ids.append(journal.get('id'))
        return journal_ids

    @api.model
    def _get_company_move(self, options):
        company_ids = []
        multi_companies = options.get('multi_company', [])
        for company in multi_companies:
            if company.get('selected', False):
                company_ids.append(company.get('id'))
        return company_ids

    @api.model
    def _get_sql_where(self, options):
        params = []
        sql_where = " WHERE 1 = 1 "
        # Date Range
        sql_where += " AND aml.date >= %s AND aml.date <= %s "
        date_range = options.get('date')
        params += [date_range.get('date_from'), date_range.get('date_to')]
        # Journal Ids
        journal_ids = self._get_journal_move(options)
        if journal_ids:
            sql_where += " AND aml.journal_id IN %s "
            params += [tuple(journal_ids)]
        company_ids = self._get_company_move(options)
        if company_ids:
            sql_where += " AND aml.company_id IN %s "
            params += [tuple(company_ids)]
        return sql_where, params

    @api.model
    def _get_sql_orderby(self, options):
        sql_orderby = " ORDER BY aa.code "
        return sql_orderby

    @api.model
    def _get_account_lines_niif_colgap(self, options):
        sql_select = self._get_sql_select(options)
        sql_from = self._get_sql_from(options)
        sql_where, params = self._get_sql_where(options)
        sql_orderby = self._get_sql_orderby(options)
        self.env.cr.execute(sql_select+sql_from+sql_where+sql_orderby, params)
        results = self.env.cr.dictfetchall()
        return results

    @api.model
    def _get_value_account(self, account_dict, line):
        if (line.get('accounting', False) == 'both'
                or line.get('accounting', False) == 'niif'):
            account_dict['amount_niif'] += line.get('balance')
        if (line.get('accounting', False) == 'fiscal'
                or line.get('accounting', False) == 'both'):
            account_dict['amount_colgap'] += line.get('balance')
        return account_dict

    @api.model
    def _get_filter_code_accounts(self, options):
        code_account_from = False
        code_account_to = False
        if (options.get('account_accounts', False)
                and options.get('account_accounts_to', False)):
            account_from_id = self.env['account.account'].browse(
                options.get('account_accounts'))
            account_to_id = self.env[
                'account.account'].browse(options.get('account_accounts_to'))
            code_account_from = account_from_id.code
            code_account_to = account_to_id.code
        return code_account_from, code_account_to

    @api.model
    def _validate_account_list(self, code_account_from, code_account_to, code):
        if (int(code) >= int(code_account_from)
                and int(code) <= int(code_account_to)):
            return True
        return False

    @api.model
    def _estructure_report(self, account, key):
        columns = []
        lines = []
        account['difference'] = (
            round(account['amount_colgap']-account['amount_niif'], 2))
        columns = [
            {'name': self.format_value(account.get(
                'amount_colgap'), blank_if_zero=True), 'class': 'number',
             'no_format_name': account.get('amount_colgap')},
            {'name': self.format_value(account.get(
                'amount_niif'), blank_if_zero=True), 'class': 'number',
             'no_format_name': account.get('amount_niif')},
            {'name': self.format_value(account.get(
                'difference'), blank_if_zero=True), 'class': 'number',
             'no_format_name': account.get('difference')}
        ]
        lines.append({
            'id': key,
            'name': "{0} {1}".format(
                    account.get('aa_code'), account.get('aa_name')),
            'title_hover': account.get('aa_name'),
            'columns': columns,
            'caret_options': 'account.account',
        })
        return lines

    @api.model
    def _get_account_line_report(self, all_accounts, options):
        lines = []
        total_niif = 0.0
        total_colgap = 0.0
        total_balance = 0.0
        code_account_from, code_account_to = (
            self._get_filter_code_accounts(options))
        for key, account in all_accounts.items():
            if not code_account_from and not code_account_to:
                lines += self._estructure_report(account, key)
                total_niif += round(account['amount_niif'], 2)
                total_colgap += round(account['amount_colgap'], 2)
                total_balance += round(account['difference'], 2)
            if (code_account_from and code_account_to
                    and self._validate_account_list(
                        code_account_from, code_account_to,
                        account['aa_code'])):
                lines += self._estructure_report(account, key)
                total_niif += round(account['amount_niif'], 2)
                total_colgap += round(account['amount_colgap'], 2)
                total_balance += round(account['difference'], 2)
        lines.append({
            'id': 'grouped_accounts_total',
            'name': _('Total'),
            'class': 'total',
            'columns': [
                {'name': self.format_value(total_colgap), 'class': 'number'},
                {'name': self.format_value(total_niif), 'class': 'number'},
                {'name': self.format_value(total_balance), 'class': 'number'}
            ],
            'level': 1,
        })
        return lines

    @api.model
    def _get_lines(self, options, line_id=None):
        account_result = self._get_account_lines_niif_colgap(options)
        all_accounts = {}
        lines = []
        for line in account_result:
            line['amount_niif'] = 0.0
            line['amount_colgap'] = 0.0
            if all_accounts.get(line.get('aa_id'), False):
                account_dict = all_accounts.get(line.get('aa_id'), False)
                account_dict = self._get_value_account(
                    account_dict, line)
                continue
            all_accounts[line.get('aa_id')] = line
            account_dict = all_accounts.get(line.get('aa_id'), False)
            account_dict = self._get_value_account(
                account_dict, line)

        lines = self._get_account_line_report(all_accounts, options)
        return lines

    def _get_report_name(self):
        return _('Difference NIIF-Colgap')
