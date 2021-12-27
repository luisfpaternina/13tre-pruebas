# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountProvisionDeteriorateReceivableSettings(models.Model):
    _name = 'account.provision.deteriorate.receivable.settings'

    accounting_type = fields.Selection(
        [
            ('niif', 'NIIF'),
            ('fiscal', 'FISCAL')
        ],
        string=_("Accounting Type"),
        required=True
    )
    percentage = fields.Float(
        string=_("Percentage"),
        required=True
    )
    first_day = fields.Integer(
        string=_("First Day"),
        required=True
    )
    number_days = fields.Integer(
        string=_("Number of Days"),
        required=True
    )
    expense_account_id = fields.Many2one(
        'account.account',
        string=_("Expense Account"),
        required=True
    )
    accumulation_account_id = fields.Many2one(
        'account.account',
        string=_("Accumulation Account"),
        required=True
    )
    recovery_account_id = fields.Many2one(
        'account.account',
        string=_("Recovery Account"),
        required=True
    )
    journal_id = fields.Many2one(
        'account.journal',
        string=_("Journal"),
        required=True
    )

    _sql_constraints = [
        (
            'unique_accounting_type_provision_deteriorate_receivable_settings',
            'unique (accounting_type)',
            (
                'You cannot create more than one setting with the same\n'
                'accounting type.'
            )
        )
    ]
