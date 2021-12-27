# -- coding: utf-8 --
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
import json
import io
from odoo import models, api, fields, _
from odoo.tools.misc import format_date
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import xlsxwriter
import logging
_logger = logging.getLogger(__name__)


class AccountReport(models.AbstractModel):
    _inherit = "account.report"
    _description = 'Account trial balance report advance'

    filter_levels_niff = None
    filter_range_account = None
    filter_levels_filter = None
    filter_levels = None

    def _get_account_journals_accounting(self, key):
        journals = self.env['account.journal'].search([('accounting','in', key)])
        # debits = journals.mapped('default_debit_account_id')
        # credits = journals.mapped('default_credit_account_id')
        # accounts = journals.mapped('default_debit_account_id') + journals.mapped('default_credit_account_id')
        # return accounts.ids or []
        return journals.ids or []

    @api.model
    def _get_options_levels_niif(self, options):
        niif = []
        # accounts = []
        journals = []
        for lvl in options.get('levels_niff'):
            if lvl.get('selected'):
                niif.append(lvl.get('id'))
        if niif:
            niif.append('both')
            journals = self._get_account_journals_accounting(niif)
            # accounts = self._get_account_journals_accounting(niif)
            # return accounts or True
            # return journals or True
        # return accounts or False
        # return journals or False
        return journals

    @api.model
    def _get_options_levels_filter(self, options):
        lvls = []
        accounts = []
        for lvl in options.get('levels_filter'):
            if lvl.get('selected'):
                lvls.append(lvl.get('id'))
        if lvls:
            accounts = self.env['account.account'].search([('level','in',lvls)]).ids or []
            return accounts or True
        return accounts or False

    @api.model
    def _get_options_domain(self, options):
        domain = super(AccountReport, self)._get_options_domain(options)
        levels, accounting = False, False
        if options.get('levels_niff'):
            journal = self._get_options_levels_niif(options)
            band = False
            position = False
            for d in range(0, len(domain)):
                if domain[d][0] == 'journal_id':
                    position = d
                    # print("********domain[d][2]",type(domain[d][2]))
                    # current = domain[d][2]
                    # domain[d][2] = tuple(current)+tuple(journal)
                    # band = True
            if journal and position:
                domain.pop(position)
                domain += [('journal_id', 'in', journal)]
            if journal and not band:
                domain += [('journal_id', 'in', journal)]
        if options.get('levels_filter'):
            levels = self._get_options_levels_filter(options)
            if levels:
                domain += [('account_id','in',levels)]

        # if levels or accounting:
        #     if levels and accounting:
        #         try:
        #             account_ids = list(set(accounting).intersection(levels))
        #         except :
        #             account_ids = []
        #     if levels and not accounting:
        #         account_ids = levels
        #     if accounting and not levels:
        #         account_ids = accounting
        #     try:
        #         account_ids = list(account_ids)
        #     except :
        #         account_ids = []
        #     domain += [('account_id','in',account_ids)]
        if options.get('range_account'):
            domain += self._get_options_range_account(options)

        return domain

    @api.model
    def _get_options_range_account(self, options):
        domain = []
        code_account_from, code_account_to = (
            self._get_filter_code_accounts(options))
        if code_account_from and code_account_to:
            domain = [('account_id.code','>=',code_account_from),('account_id.code','<=',code_account_to)]
        return domain

    @api.model
    def _init_filter_levels_niff(self, options, previous_options=None):
        if self.filter_levels_niff is None:
            return

        if  previous_options and previous_options.get('levels_niff'):
            accounting_map = dict((opt['id'], opt['selected']) for opt in previous_options.get('levels_niff') if 'selected' in opt)
        else:
            accounting_map = {}
        options['levels_niff'] = [
            {'id': 'niif', 'name': 'NIIF', 'selected': accounting_map.get('niif')},
            {'id': 'fiscal', 'name': 'Fiscal', 'selected': accounting_map.get('fiscal')},
        ]

    @api.model
    def _init_filter_levels_filter(self, options, previous_options=None):
        if self.filter_levels_filter is None:
            return

        if previous_options and previous_options.get('levels_filter'):
            levels_map = dict(
                (opt['id'], opt['selected'])for opt in
                previous_options.get('levels_filter') if 'selected' in opt)
        else:
            levels_map = {}
        options['levels_filter'] = [
            {'id': "1", 'name': "Level 1", 'selected': levels_map.get("1")},
            {'id': "2", 'name': "Level 2", 'selected': levels_map.get("2")},
            {'id': "3", 'name': "Level 3", 'selected': levels_map.get("3")},
            {'id': "4", 'name': "Level 4", 'selected': levels_map.get("4")},
            {'id': "5", 'name': "Level 5", 'selected': levels_map.get("5")},
            {'id': "6", 'name': "Level 6", 'selected': levels_map.get("6")},
            {'id': "7", 'name': "Level 7", 'selected': levels_map.get("7")},
            {'id': "8", 'name': "Level 8", 'selected': levels_map.get("8")},
            {'id': "9", 'name': "Level 9", 'selected': levels_map.get("9")},
            {'id': "10", 'name': "Level 10", 'selected': levels_map.get("10")},
            {'id': "11", 'name': "Level 11", 'selected': levels_map.get("11")},
            {'id': "12", 'name': "Level 12", 'selected': levels_map.get("12")},
        ]

    # @api.model
    # def _init_filter_account_level(self, options, previous_options=None):
    #     if not self.filter_account_level:
    #         return

    #     if previous_options and previous_options.get('account_levels'):
    #         account_levels_map = dict(
    #             (opt['code'],
    #             opt['selected'])
    #           for opt in previous_options['account_levels'])
    #     else:
    #         account_levels_map = {}

    #     options['account_levels'] = []
    #     levels = self.env['ir.model.fields'].search([
    #         ("name", "=", "level"),
    #         ("model", "=", "account.account")
    #     ])
    #     for level in levels.selection_ids:
    #         options['account_levels'].append({
    #             'id': level.id,
    #             'code': level.value,
    #             'name': level.name,
    #             'selected': account_levels_map.get(
    #                 level.value),
    #         })

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

    # @api.model
    # def _validate_account_list(
    #   self, code_account_from, code_account_to, code):
    #     if (int(code) >= int(code_account_from)
    #             and int(code) <= int(code_account_to)):
    #         return True
    #     return False

    # @api.model
    # def _get_filter_journals(self):
    #     return self.env['account.journal'].with_context(
    #       active_test=False).search([
    #         ('company_id', 'in',
    #           self.env.user.company_ids.ids or [self.env.company.id])
    #     ], order="company_id, name")

    # @api.model
    # def _init_filter_journals(self, options, previous_options=None):
    #     if self.filter_journals is None:
    #         return

    # @api.model
    # def _init_filter_accounting_type(self, options, previous_options=None):
    #     if not self.filter_accounting_type:
    #         return

    #     #options_filter = self.filter_accounting_type.get('filter')
    #     #fiscal = self.filter_accounting_type.get('fiscal')
    #     #niif = self.filter_accounting_type.get('niif')

    # Create codes path in the hierarchy based on account.
    def get_account_levels(self, account):
        # A code is tuple(sort priority, actual code)
        codes = []
        level = {
            "1": _("Level 1"),
            "2": _("Level 2"),
            "3": _("Level 3"),
            "4": _("Level 4"),
            "5": _("Level 5"),
            "6": _("Level 6"),
            "7": _("Level 7"),
            "8": _("Level 8"),
            "9": _("Level 9"),
            "10": _("Level 10"),
            "11": _("Level 11"),
            "12": _("Level 12")}
        if account.level:
            codes.append((self.MOST_SORT_PRIO, level[account.level]))
            # group = account.group_id
            # while group:
            #     code = '%s %s' % (group.code_prefix or '', group.name)
            #     codes.append((self.MOST_SORT_PRIO, code))
            #     group = group.parent_id
        else:
            # Limit to 3 levels.
            code = account.code[:3]
            while code:
                codes.append((self.MOST_SORT_PRIO, code))
                code = code[:-1]
        return list(reversed(codes))

    @api.model
    def _create_levels(self, lines, options):
        """This method is called when the option 'hiearchy' is enabled on a
        report. It receives the lines (as computed by _get_lines()) in
        argument, and will add a hiearchy in those lines by using the
        account.group of accounts. If not set, it will fallback on creating a
        hierarchy based on the account's code first 3 digits.
        """
        # Avoid redundant browsing.
        accounts_cache = {}

        # Retrieve account either from cache, either by browsing.
        def get_account(id):
            if id not in accounts_cache:
                accounts_cache[id] = self.env['account.account'].browse(id)
            return accounts_cache[id]

        # Add the report line to the hierarchy recursively.
        def add_line_to_hierarchy(line, codes, level_dict, depth=None):
            # Recursively build a dict where:
            # 'children' contains only subcodes
            # 'lines' contains the lines at this level
            # This > lines [optional, i.e. not for topmost level]
            #      > children > [codes] "That" > lines
            #                                  > metadata
            #                                  > children
            #      > metadata(depth, parent ...)

            if not codes:
                return
            if not depth:
                depth = line.get('level', 1)
            level_dict.setdefault('depth', depth)
            level_dict.setdefault(
                'parent_id', 'hierarchy_' + codes[0][1]
                if codes[0][0] != 'root' else codes[0][1])
            level_dict.setdefault('children', {})
            code = codes[1]
            codes = codes[1:]
            level_dict['children'].setdefault(code, {})

            if len(codes) > 1:
                add_line_to_hierarchy(
                    line, codes, level_dict['children'][code], depth=depth + 1)
            else:
                level_dict['children'][code].setdefault('lines', [])
                level_dict['children'][code]['lines'].append(line)
                line['level'] = depth + 1
                for l in level_dict['children'][code]['lines']:
                    l['parent_id'] = 'hierarchy_' + code[1]

        # Merge a list of columns together and take care about str values.
        def merge_columns(columns):
            return [
                ('n/a' if any(i != '' for i in x) else '')
                if any(isinstance(i, str) for i in x)
                else sum(x) for x in zip(*columns)]

        # Get_lines for the newly computed hierarchy.
        def get_hierarchy_lines(values, depth=1):
            lines = []
            sum_sum_columns = []
            unfold_all = self.env.context.get(
                'print_mode') and len(options.get('unfolded_lines')) == 0
            for base_line in values.get('lines', []):
                lines.append(base_line)
                sum_sum_columns.append(
                    [c.get('no_format_name', c['name'])
                        for c in base_line['columns']])

            # For the last iteration, there might not be the children key
            # (see add_line_to_hierarchy)
            for key in sorted(values.get('children', {}).keys()):
                sum_columns, sub_lines = get_hierarchy_lines(
                    values['children'][key], depth=values['depth'])
                id = 'hierarchy_' + key[1]
                header_line = {
                    'id': id,
                    'name':
                        key[1] if len(key[1]) < 60 else key[1][:60] + '...',
                    'title_hover': key[1],
                    'unfoldable': True,
                    'unfolded':
                        id in options.get('unfolded_lines') or unfold_all,
                    'level': values['depth'],
                    'parent_id': values['parent_id'],
                    'columns': [
                        {
                            'name':
                            self.format_value(c)
                            if not isinstance(c, str) else c
                        } for c in sum_columns],
                }
                if key[0] == self.LEAST_SORT_PRIO:
                    header_line['style'] = 'font-style:italic;'
                lines += [header_line]
                if header_line.get(
                        'unfolded') or not self._context.get('print_mode'):
                    lines += sub_lines
                sum_sum_columns.append(sum_columns)
            return merge_columns(sum_sum_columns), lines

        def deep_merge_dict(source, destination):
            for key, value in source.items():
                if isinstance(value, dict):
                    # get node or create one
                    node = destination.setdefault(key, {})
                    deep_merge_dict(value, node)
                else:
                    destination[key] = value

            return destination

        # Hierarchy of codes.
        accounts_hierarchy = {}

        new_lines = []
        no_group_lines = []
        # If no account.group at all, we need to pass once again in the loop to
        # dispatch
        # all the lines across their account prefix, hence the None
        for line in lines + [None]:
            # Only deal with lines grouped by accounts.
            # And discriminating sections defined by
            # account.financial.html.report.line
            is_grouped_by_account = line and (
                line.get('caret_options') == 'account.account'
                or line.get('account_id'))
            if not is_grouped_by_account or not line:

                # No group code found in any lines, compute it automatically.
                no_group_hierarchy = {}
                for no_group_line in no_group_lines:
                    codes = [
                        ('root', str(line.get('parent_id')) or 'root')
                        if line else 'root',
                        (self.LEAST_SORT_PRIO, _('(No Group)'))]
                    if not accounts_hierarchy:
                        account = get_account(
                            no_group_line.get(
                                'account_id',
                                self._get_caret_option_target_id(
                                    no_group_line.get('id'))))
                        codes = [
                            ('root',
                                line and str(line.get('parent_id'))
                                or 'root')] + self.get_account_levels(account)
                    add_line_to_hierarchy(
                        no_group_line,
                        codes,
                        no_group_hierarchy,
                        line and line.get('level') or 0 + 1)
                no_group_lines = []

                deep_merge_dict(no_group_hierarchy, accounts_hierarchy)

                # Merge the newly created hierarchy with existing lines.
                if accounts_hierarchy:
                    new_lines += get_hierarchy_lines(accounts_hierarchy)[1]
                    accounts_hierarchy = {}

                if line:
                    new_lines.append(line)
                continue

            # Exclude lines having no group.
            account = get_account(
                line.get(
                    'account_id',
                    self._get_caret_option_target_id(line.get('id'))))
            if not account.group_id:
                no_group_lines.append(line)
                continue

            codes = [
                ('root', str(line.get('parent_id')) or 'root')
                ] + self.get_account_levels(account)
            add_line_to_hierarchy(
                line, codes, accounts_hierarchy, line.get('level', 0) + 1)

        return new_lines

    def get_html_levels(self, options, line_id=None, additional_context=None):
        '''
        return the html value of report, or html value of unfolded line
        * if line_id is set, the template used will be the line_template
        otherwise it uses the main_template. Reason is for efficiency,
        when unfolding a line in the report we don't want to reload all lines,
        just get the one we unfolded.
        '''
        # Check the security before updating the context to make sure the
        # options are safe.
        self._check_report_security(options)

        # Prevent inconsistency between options and context.
        self = self.with_context(self._set_context(options))

        templates = self._get_templates()
        report_manager = self._get_report_manager(options)
        report = {
            'name': self._get_report_name(),
            'summary': report_manager.summary,
            'company_name': self.env.company.name}
        lines = self._get_lines(options, line_id=line_id)

        lines = self._create_levels(lines, options)

        footnotes_to_render = []
        if self.env.context.get('print_mode', False):
            # we are in print mode, so compute footnote number and include them
            # in lines values, otherwise, let the js compute the number
            # correctly as we don't know all the visible lines.
            footnotes = dict(
                [(str(f.line), f) for f in report_manager.footnotes_ids])
            number = 0
            for line in lines:
                f = footnotes.get(str(line.get('id')))
                if f:
                    number += 1
                    line['footnote'] = str(number)
                    footnotes_to_render.append(
                        {'id': f.id, 'number': number, 'text': f.text})

        rcontext = {'report': report,
                    'lines':
                        {
                            'columns_header': self.get_header(options),
                            'lines': lines},
                    'options': options,
                    'context': self.env.context,
                    'model': self}
        if additional_context and type(additional_context) == dict:
            rcontext.update(additional_context)
        if self.env.context.get('analytic_account_ids'):
            rcontext['options']['analytic_account_ids'] = [
                {'id': acc.id, 'name': acc.name}
                for acc in self.env.context['analytic_account_ids']
            ]

        render_template = templates.get(
            'main_template', 'account_reports.main_template')
        if line_id is not None:
            render_template = templates.get(
                'line_template', 'account_reports.line_template')
        html = self.env['ir.ui.view'].render_template(
            render_template,
            values=dict(rcontext),
        )
        if self.env.context.get('print_mode', False):
            for k, v in self._replace_class().items():
                html = html.replace(k, v)
            # append footnote as well
            html = html.replace(
                b'<div class="js_account_report_footnotes"></div>',
                self.get_html_footnotes(footnotes_to_render))
        return html

    def get_html(self, options, line_id=None, additional_context=None):
        if options.get('levels'):
            return self.get_html_levels(
                options, line_id=None, additional_context=None)
        else:
            return super(AccountReport, self).get_html(
                options, line_id=line_id,
                additional_context=additional_context)

    # Create codes path in the hierarchy based on account.
    def get_account_codes(self, account):
        # A code is tuple(sort priority, actual code)
        codes = []
        if account.group_id:
            group = account.group_id
            while group:
                code = '%s %s' % (group.code_prefix or '', group.name)
                codes.append((self.MOST_SORT_PRIO, code))
                group = group.parent_id
        else:
            # Limit to 4 levels.
            code = account.code[:6]
            while code:
                codes.append((self.MOST_SORT_PRIO, code))

                # Excluir cantidad de dígitos 3, 5
                code = (code[:-1]
                        if len(code[:-1]) != 3 and len(code[:-1]) != 5
                        else code[:-2])
        return list(reversed(codes))

    @api.model
    def _create_hierarchy(self, lines, options):
        """This method is called when the option 'hiearchy' is enabled on a
        report. It receives the lines (as computed by _get_lines()) in
        argument, and will add a hiearchy in those lines by using the
        account.group of accounts. If not set, it will fallback on creating a
        hierarchy based on the account's code first 3 digits.
        """
        # Avoid redundant browsing.
        accounts_cache = {}

        # Retrieve account either from cache, either by browsing.
        def get_account(id):
            if id not in accounts_cache:
                accounts_cache[id] = self.env['account.account'].browse(id)
            return accounts_cache[id]

        # Add the report line to the hierarchy recursively.
        def add_line_to_hierarchy(line, codes, level_dict, depth=None):
            # Recursively build a dict where:
            # 'children' contains only subcodes
            # 'lines' contains the lines at this level
            # This > lines [optional, i.e. not for topmost level]
            #      > children > [codes] "That" > lines
            #                                  > metadata
            #                                  > children
            #      > metadata(depth, parent ...)

            if not codes:
                return
            if not depth:
                depth = line.get('level', 1)
            level_dict.setdefault('depth', depth)
            level_dict.setdefault(
                'parent_id', 'hierarchy_' + codes[0][1]
                if codes[0][0] != 'root' else codes[0][1])
            level_dict.setdefault('children', {})
            code = codes[1]
            codes = codes[1:]

            level_dict['children'].setdefault(code, {})

            if len(codes) > 1:
                add_line_to_hierarchy(
                    line, codes, level_dict['children'][code], depth=depth + 1)
            else:
                level_dict['children'][code].setdefault('lines', [])
                level_dict['children'][code]['lines'].append(line)
                line['level'] = depth + 1
                for l in level_dict['children'][code]['lines']:
                    l['parent_id'] = 'hierarchy_' + code[1]

        # Merge a list of columns together and take care about str values.
        def merge_columns(columns):
            return [
                ('n/a' if any(i != '' for i in x) else '')
                if any(isinstance(i, str) for i in x) else sum(x)
                for x in zip(*columns)]

        # Get_lines for the newly computed hierarchy.
        def get_hierarchy_lines(values, depth=1):
            lines = []
            sum_sum_columns = []
            unfold_all = (
                self.env.context.get('print_mode')
                and len(options.get('unfolded_lines')) == 0)
            for base_line in values.get('lines', []):
                lines.append(base_line)
                sum_sum_columns.append(
                    [c.get(
                        'no_format_name',
                        c['name']) for c in base_line['columns']])

            # For the last iteration, there might not be the children key
            # (see add_line_to_hierarchy)
            for key in sorted(values.get('children', {}).keys()):
                sum_columns, sub_lines = get_hierarchy_lines(
                    values['children'][key], depth=values['depth'])
                id = 'hierarchy_' + key[1]
                name = self.env['account.account'].search([
                    ("code", "=", key[1])
                ])
                name = key[1] + " " + name.name if name else key[1]
                header_line = {
                    'id': id,
                    'name': name if len(name) < 60 else name[:60] + '...',
                    'title_hover': key[1],
                    'unfoldable': True,
                    'unfolded':
                        id in options.get('unfolded_lines') or unfold_all,
                    'level': values['depth'],
                    'parent_id': values['parent_id'],
                    'columns': [
                        {
                            'name':
                            self.format_value(c)
                            if not isinstance(c, str) else c
                        } for c in sum_columns]
                }
                if key[0] == self.LEAST_SORT_PRIO:
                    header_line['style'] = 'font-style:italic;'
                lines += [header_line]
                if (header_line.get('unfolded')
                        or not self._context.get('print_mode')):
                    lines += sub_lines
                sum_sum_columns.append(sum_columns)
            return merge_columns(sum_sum_columns), lines

        def deep_merge_dict(source, destination):
            for key, value in source.items():
                if isinstance(value, dict):
                    # get node or create one
                    node = destination.setdefault(key, {})
                    deep_merge_dict(value, node)
                else:
                    destination[key] = value

            return destination

        # Hierarchy of codes.
        accounts_hierarchy = {}

        new_lines = []
        no_group_lines = []
        # If no account.group at all, we need to pass once again in the
        # loop to dispatch all the lines across their account prefix,
        # hence the None
        for line in lines + [None]:
            # Only deal with lines grouped by accounts.
            # And discriminating sections defined by
            # account.financial.html.report.line
            is_grouped_by_account = line and (
                line.get('caret_options') == 'account.account'
                or line.get('account_id'))
            if not is_grouped_by_account or not line:

                # No group code found in any lines, compute it automatically.
                no_group_hierarchy = {}
                for no_group_line in no_group_lines:
                    codes = [
                        ('root', str(line.get('parent_id')) or 'root')
                        if line else 'root',
                        (self.LEAST_SORT_PRIO, _('(No Group)'))]

                    if not accounts_hierarchy:
                        account = get_account(
                            no_group_line.get(
                                'account_id',
                                self._get_caret_option_target_id(
                                    no_group_line.get('id'))))
                        codes = [
                            (
                                'root',
                                line and str(line.get('parent_id')) or 'root')
                            ] + self.get_account_codes(account)

                    add_line_to_hierarchy(
                        no_group_line, codes, no_group_hierarchy,
                        line and line.get('level') or 0 + 1)
                no_group_lines = []

                deep_merge_dict(no_group_hierarchy, accounts_hierarchy)

                # Merge the newly created hierarchy with existing lines.
                if accounts_hierarchy:
                    new_lines += get_hierarchy_lines(accounts_hierarchy)[1]
                    accounts_hierarchy = {}

                if line:
                    new_lines.append(line)
                continue

            # Exclude lines having no group.
            account = get_account(
                line.get(
                    'account_id',
                    self._get_caret_option_target_id(line.get('id'))))
            if not account.group_id:
                no_group_lines.append(line)
                continue

            codes = [
                ('root', str(line.get('parent_id')) or 'root')
                ] + self.get_account_codes(account)
            add_line_to_hierarchy(
                line, codes, accounts_hierarchy, line.get('level', 0) + 1)

        return new_lines
