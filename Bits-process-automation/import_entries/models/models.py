# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class account_move_line_import(models.Model):
    _inherit='account.move'
    name=fields.Char(string='Number',required=True,readonly=False,copy=False,default='/')
    
    def _check_balanced(self):
        x=0

class account_move_line_import(models.Model):
    _inherit='account.move.line'
    move_id=fields.Many2one('account.move', string='Journal Entry',index=True,required=True,readonly=False,auto_join=True,ondelete="cascade",help="The move of this entry line.")
    debit_import=fields.Monetary(string='Import debit',default=0.0,currency_field='company_currency_id')
    credit_import=fields.Monetary(string='Import credit',default=0.0,currency_field='company_currency_id')
