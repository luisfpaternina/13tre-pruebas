# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.modules.module import get_module_resource


class AccountMovePartnerIva(models.Model):
    _inherit = "account.move"

    @api.model
    def _get_tax_grouping_key_from_tax_line(self, tax_line):
        ''' Add partner_id to the dictionary created '''
        res = super()._get_tax_grouping_key_from_tax_line(tax_line)
        res['partner_id'] = tax_line.partner_id.id
        return res

    @api.model
    def _get_tax_grouping_key_from_base_line(self, base_line, tax_line):
        ''' Add partner_id to the dictionary created '''
        res = super()._get_tax_grouping_key_from_base_line(base_line, tax_line)
        res['partner_id'] = base_line.partner_id.id
        return res

    @api.model
    def _get_tax_key_for_group_add_base(self, line):
        tax_key = super(
            AccountMovePartnerIva, self)._get_tax_key_for_group_add_base(line)

        tax_key += [
            line.partner_id.id,
        ]
        return tax_key

    @api.onchange('line_ids')
    def _recompute_taxes_on_delete(self):
        self._recompute_dynamic_lines(True, True)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange('amount_currency', 'currency_id', 'debit', 'credit',
                  'tax_ids', 'account_id', 'price_unit', 'partner_id')
    def _onchange_mark_recompute_taxes(self):
        ''' Add partner_id in change event to recompute taxes '''
        super(AccountMoveLine, self)._onchange_mark_recompute_taxes()
