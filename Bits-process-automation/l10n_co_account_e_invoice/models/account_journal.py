# coding: utf-8
# LISTO
from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    debit_note = fields.Boolean()
