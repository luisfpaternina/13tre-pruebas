# -*- coding: utf-8 -*-
from ast import literal_eval
from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    adjusment_entry_account_analytic = fields.Many2one(
        'account.analytic.account',
        string='Adjusment Entry Account Analytic',
        related='company_id.adjusment_entry_account_analytic',
        readonly=False
    )
    account_type_equity = fields.Boolean(
        string='Equity',
        related='company_id.account_type_equity',
        readonly=False
    )
    account_type_asset = fields.Boolean(
        string='Asset',
        related='company_id.account_type_asset',
        readonly=False
    )
    account_type_liability = fields.Boolean(
        string='Liability',
        related='company_id.account_type_liability',
        readonly=False
    )
    account_type_income = fields.Boolean(
        string='Income',
        related='company_id.account_type_income',
        readonly=False
    )
    account_type_expense = fields.Boolean(
        string='Expense',
        related='company_id.account_type_expense',
        readonly=False
    )
    account_type_off_balance = fields.Boolean(
        string='Off Balance',
        related='company_id.account_type_off_balance',
        readonly=False
    )


class ResCompany(models.Model):
    _inherit = 'res.company'

    adjusment_entry_account_analytic = fields.Many2one(
        'account.analytic.account',
        string='Adjusment Entry Account Analytic'
    )
    account_type_equity = fields.Boolean(
        string='Equity',
    )
    account_type_asset = fields.Boolean(
        string='Asset',
    )
    account_type_liability = fields.Boolean(
        string='Liability',
    )
    account_type_income = fields.Boolean(
        string='Income',
    )
    account_type_expense = fields.Boolean(
        string='Expense',
    )
    account_type_off_balance = fields.Boolean(
        string='Off Balance',
    )
