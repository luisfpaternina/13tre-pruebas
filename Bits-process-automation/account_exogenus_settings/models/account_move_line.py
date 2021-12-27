from odoo import api, fields, models, _
from odoo.tools.misc import xlwt
import base64
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
import xlsxwriter
import logging
from operator import itemgetter
from itertools import groupby
from io import BytesIO
_logger = logging.getLogger(__name__)


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    concept = fields.Char('Concept', compute="_compute_concept", store=True)

    @api.depends('account_id')
    def _compute_concept(self):
        for record in self:
            concept_model = self.env['account.concept.exogenus.line'].search([(
                'account_id', '=', record.account_id.id)])
            record.concept = concept_model.name

    def agroup_concept(self):
        account_ml_obj = self.env['account.move.line'].search([])
        for record in self:
            concepts = account_ml_obj.\
                filtered(
                    lambda p: p.concept == record.concept
                    and p.partner_id == record.partner_id)

        return concepts

    def _get_columns_totaL_accounts(self):
        sum_partner = []
        sum_account = []
        partners = self.env['res.partner'].search([])
        for partner in partners:
            accounts = self.env['account.move.line'].search(
                [('partner_id', '=', partner.id)])
            if accounts:
                accounts_partner = accounts.filtered(
                    lambda p: p.partner_id.id == partner.id)
                accounts_array = set(
                    [x.account_id.id for x in accounts_partner])
                accounts_array_m = []
                for id in accounts_array:
                    if id not in accounts_array_m:
                        accounts_array_m.append(id)

                for account_id in accounts_array_m:
                    accounts_accounts = accounts.filtered(
                        lambda p: p.account_id.id == account_id)
                    total_debit = sum([x.debit for x in accounts_accounts])
                    sum_account.append(total_debit)

        return sum_account
