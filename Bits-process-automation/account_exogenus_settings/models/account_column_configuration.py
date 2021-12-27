# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import Warning, ValidationError
from operator import itemgetter
from itertools import groupby
import logging


class AccountColumnConfiguration(models.Model):
    _name = 'account.column.configuration'
    _description = 'Account column configuration'

    name = fields.Char(string="Name")
    account_colum_line_ids = fields.One2many(
        'account.column.configuration.lines',
        'account_column_id',
        string="account column configuration lines")
    code = fields.Char(string="Code")
    description = fields.Text(string="Description")
    # condition_select = fields.Selection([('none','always true'),
    # ('python','python expression')],string="Condition select")
    condition_python = fields.Text(
        string="Condition python",
        default="result = object.name")
    account_account_ids = fields.Many2many(
        'account.account',
        string="Accounts")
    format_exogenus_id = fields.Many2one(
        'account.format.exogenus',
        string="Format Exogenus")
    bool_delete = fields.Boolean(
        string="Column to calculate taxes"
    )

    def execute_code(self, move_line, wiz):
        localdict = {
            'object': move_line,
            'user_obj': self.env.user,
            'wiz': wiz,
            'self': self,
            'var1': None,
            'var2': None,
            'var3': None,
            'var4': None,
            'var5': None
            }
        try:
            exec(self.condition_python, localdict)
            return localdict.get('result', False)
        except Exception as e:
            return "Error %s: value %s" % (self.name, str(e))


class AccountColumnConfigurationLines(models.Model):
    _name = 'account.column.configuration.lines'
    _description = 'Account column configuration lines'

    column = fields.Char(string="Column")
    account = fields.Integer(string_="Account")
    account_column_id = fields.Many2one(
        'account.column.configuration',
        string="Account column configuration")


class AccountExogenusFormatColumn(models.Model):
    _name = 'account.exogenus.format.column'
    _description = 'Account exogenus format column'

    account_format_id = fields.Many2one(
        'account.format.exogenus',
        string="Format")
    account_column_id = fields.Many2one(
        'account.column.configuration',
        string="Column")
    sequence = fields.Integer(string="Sequence")
