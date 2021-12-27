# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date


class AccountAccountingClosingSettings(models.Model):
    _inherit = 'account.fiscal.year'

    journal = fields.Many2one(
        'account.journal', required=True, string=_('Journal'))
    profit_account_year = fields.Many2one(
        'account.account', required=True, string=_('Profit account year'))
    account_lost_year = fields.Many2one(
        'account.account', required=True, string=_('Account lost year'))
    reference = fields.Char(required=True, string=_('Reference'), size=150)

    journal_items_count = fields.Integer(
        string="Journal Items",
        compute="_compute_journal_items_count"
    )
    move_id = fields.Many2one(
        'account.move',
        readonly=True,
        index=True,
        string=_("Journal Entry")
    )

    # Execute accounintg close process
    def execute_accounting_close(self):
        options = dict()
        options["date"] = dict(
            date_from=self.date_from,
            date_to=self.date_to
        )
        options["parent_state"] = "posted"
        options["company_id"] = self.company_id.id
        options["journal_id"] = self.journal.id
        options["ref"] = self.reference
        options["allows_accounting_closing"] = "true"

        self.move_id.line_ids.unlink()
        self.move_id.unlink()
        journal_entry = self._create_journal_entry(options)
        result = self._execute_sql_query(options)
        debit_amount = 0
        credit_amount = 0
        journal_items = []

        for line in result:
            journal_item = self._create_journal_item(line)
            debit_amount += journal_item["debit"]
            credit_amount += journal_item["credit"]
            journal_items.append((0, 0, journal_item))

        journal_items.append((0, 0, self._create_end_journal_item(
            debit_amount, credit_amount)))
        journal_entry['line_ids'] = journal_items
        self.move_id = self.env['account.move'].create(journal_entry)

        return False

    # Create end journal item
    def _create_end_journal_item(self, debit_amount, credit_amount):
        difference = debit_amount - credit_amount
        values = dict()
        values["move_id"] = self.move_id.id
        values["partner_id"] = self.company_id.id
        values["debit"] = 0
        values["credit"] = 0
        values["name"] = _(
            "Income statements cancellation (") + self.name + ")"

        if difference >= 0:
            values["account_id"] = self.profit_account_year.id
            values["credit"] = abs(difference)
        else:
            values["account_id"] = self.account_lost_year.id
            values["debit"] = abs(difference)

        return values

    # Create journal item
    def _create_journal_item(self, options):
        values = dict()
        values["move_id"] = self.move_id.id
        values["account_id"] = options.get("aml_account_id", False)
        values["partner_id"] = options.get("aml_partner_id", False)
        values["debit"] = 0
        values["credit"] = 0
        values["name"] = _(
            "Income statements cancellation (") + self.name + ")"
        difference = options.get("aml_difference", False)

        if difference <= 0:
            values["debit"] = abs(difference)
        else:
            values["credit"] = abs(difference)

        return values

    # Create journal entry
    def _create_journal_entry(self, options):
        return {
            'ref': options.get('ref'),
            'journal_id': options.get('journal_id'),
            'company_id': options.get('company_id')
        }

    # Get amount of journal items
    def _compute_journal_items_count(self):
        for record in self:
            record.journal_items_count = len(record.move_id.line_ids)

    # Create query
    @api.model
    def _get_sql_outer_select(self):
        sql_select = (
            "SELECT "
            "CONCAT(aa.code, ' ', aa.name) AS aa_display_name, "
            "inq.aml_account_id AS aml_account_id, "
            "inq.aml_partner_id AS aml_partner_id, "
            "aa.name AS aa_name, "
            "rp.name AS rp_name, "
            "inq.aml_debit AS aml_debit, "
            "inq.aml_credit AS aml_credit, "
            "inq.aml_difference AS aml_difference "
        )
        return sql_select

    @api.model
    def _get_sql_outer_from(self):
        inner_sql = self._get_sql_select()
        inner_sql += self._get_sql_from()
        inner_sql += self._get_sql_where()
        inner_sql += self._get_sql_groupby()
        sql_from = (
            " FROM (" + inner_sql + ") AS inq "
            "LEFT JOIN account_account AS aa ON aa.id=inq.aml_account_id "
            "LEFT JOIN res_partner AS rp ON rp.id=inq.aml_partner_id "
        )
        return sql_from

    @api.model
    def _get_sql_select(self):
        sql_select = (
            " SELECT "
            "aml.account_id AS aml_account_id, "
            "aml.partner_id AS aml_partner_id, "
            "SUM(aml.debit) AS aml_debit, "
            "SUM(aml.credit) AS aml_credit, "
            "(SUM(aml.debit) - SUM(aml.credit)) AS aml_difference "
        )
        return sql_select

    @api.model
    def _get_sql_from(self):
        sql_from = (
            " FROM account_move_line AS aml "
            " LEFT JOIN account_account AS aa ON aa.id = aml.account_id"
        )
        return sql_from

    @api.model
    def _get_sql_where(self):
        sql_where = " WHERE 1 = 1 "
        sql_where += " AND aml.date >= %s AND aml.date <= %s"
        sql_where += " AND aml.parent_state = %s"
        sql_where += " AND aml.company_id = %s"
        sql_where += " AND aa.allows_accounting_closing = %s"
        return sql_where

    @api.model
    def _get_sql_groupby(self):
        sql_orderby = " GROUP BY aml.account_id, aml.partner_id "
        return sql_orderby

    @api.model
    def _get_sql_outer_where(self, options):
        params = []
        sql_where = " WHERE 1 = 1 "
        date_range = options.get('date')
        params += [
            date_range.get('date_from'),
            date_range.get('date_to'),
            options.get('parent_state'),
            options.get('company_id'),
            options.get('allows_accounting_closing')]
        return sql_where, params

    @api.model
    def _get_sql_outer_orderby(self):
        sql_orderby = " ORDER BY aa.code, rp_name "
        return sql_orderby

    @api.model
    def _get_sql_outer_limit(self):
        sql_limit = "  "
        return sql_limit

    @api.model
    def _execute_sql_query(self, options):
        sql_select = self._get_sql_outer_select()
        sql_from = self._get_sql_outer_from()
        sql_where, params = self._get_sql_outer_where(options)
        sql_orderby = self._get_sql_outer_orderby()
        sql_limit = self._get_sql_outer_limit()
        self.env.cr.execute(
            sql_select +
            sql_from +
            sql_where +
            sql_orderby +
            sql_limit, params)
        results = self.env.cr.dictfetchall()
        return results

    # Method show view
    def journal_items_view(self):
        self.ensure_one()
        domain = [
            ('move_id', '=', self.move_id.id)]
        return {
            'name': _('Journal Items'),
            'domain': domain,
            'res_model': 'account.move.line',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree',
            'limit': 80,
            'context': "{'default_employee_id': '%s'}" % self.id
        }
