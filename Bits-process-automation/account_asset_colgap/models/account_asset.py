# -*- coding: utf-8 -*-
import calendar
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.tools import float_compare, float_is_zero, float_round


class AccountAsesetColgap(models.Model):
    _inherit = 'account.asset'

    salvage_value_colgap = fields.Monetary(
        string='Not Depreciable Value colgap', digits=0, readonly=True,
        states={'draft': [('readonly', False)]},
        help="It is the amount you plan to have that you cannot "
        "depreciate colgap.")
    original_value_colgap = fields.Monetary(
        string='Original Value Colgap', digits=0,
        states={'draft': [('readonly', False)]},
        help="Original Value for Colgap")
    gross_increase_value_colgap = fields.Monetary(
        string="Gross Increase Value", compute="_compute_book_value_colgap",
        compute_sudo=True)
    method_colgap = fields.Selection(
        [('linear', 'Linear'), ('degressive', 'Degressive'),
         ('degressive_then_linear', 'Accelerated Degressive')],
        string='Method colgap', readonly=True, states={'draft': [
            ('readonly', False)], 'model': [('readonly', False)]},
        default='linear')
    method_number_colgap = fields.Integer(
        string='Number of Depreciations colgap', readonly=True,
        states={'draft': [('readonly', False)], 'model': [
            ('readonly', False)]}, default=5,
        help=("The number of depreciations needed to depreciate "
              "your asset colgap"))
    method_period_colgap = fields.Selection(
        [('1', 'Months'), ('12', 'Years')],
        string='Number of Months in a Period colgap', readonly=True,
        default='12', states={'draft': [('readonly', False)],
                              'model': [('readonly', False)]},
        help="The amount of time between two depreciations")
    account_asset_colgap_id = fields.Many2one(
        'account.account',
        string='Fixed Asset Account colgap',
        compute='_compute_value',
        help="Account used to record the purchase of the asset at "
        "its original price colgap.",
        store=True,
        states={'draft': [('readonly', False)],
                'model': [('readonly', False)]},
        domain="[('company_id', '=', company_id)]")
    account_depreciation_colgap_id = fields.Many2one(
        'account.account', string='Depreciation Account colgap',
        readonly=True, states={'draft': [('readonly', False)],
                               'model': [('readonly', False)]},
        domain="[('internal_type', '=', 'other'), ('deprecated', '=', False),"
        " ('company_id', '=', company_id)]",
        help=("Account used in the depreciation entries, to decrease the "
              "asset value colgap."))
    account_depreciation_expense_colgap_id = fields.Many2one(
        'account.account', string='Expense Account Colgap',
        readonly=True, states={'draft': [('readonly', False)],
                               'model': [('readonly', False)]},
        domain="[('internal_type', '=', 'other'), ('deprecated', '=', False), "
        "('company_id', '=', company_id)]",
        help=("Account used in the periodical entries, to record a part of"
              "the asset as expense."))
    journal_colgap_id = fields.Many2one(
        'account.journal', string='Journal colgap', readonly=True,
        states={'draft': [('readonly', False)],
                'model': [('readonly', False)]},
        domain="[('type', '=', 'general'), ('company_id', '=', company_id)]")
    value_residual_colgap = fields.Monetary(string='Depreciable Value colgap',
                                            digits=0, readonly="1")
    book_value_colgap = fields.Monetary(
        string='Book Value colgap', readonly=True,
        compute='_compute_book_value_colgap', store=True,
        help=("Sum of the depreciable value, the salvage value and the "
              "book value of all value increase items"))
    method_progress_factor_colgap = fields.Float(
        string='Degressive Factor colgap',
        readonly=True, default=0.3,
        states={'draft': [('readonly', False)],
                'model': [('readonly', False)]})
    depreciation_move_colgap_ids = fields.One2many(
        'account.move', 'asset_id', string='Depreciation Lines colgap',
        readonly=True, states={'draft': [('readonly', False)],
                               'open': [('readonly', False)],
                               'paused': [('readonly', False)]},
        domain=[('colgap', '=', True)])
    original_move_line_colgap_ids = fields.One2many(
        'account.move.line', 'asset_id', string='Journal Items',
        readonly=True, states={'draft': [('readonly', False)]}, copy=False,
        domain=[('colgap', '=', True)])

    # Links with entries
    depreciation_move_ids = fields.One2many(
        'account.move', 'asset_id', string='Depreciation Lines',
        readonly=True, states={'draft': [('readonly', False)],
                               'open': [('readonly', False)],
                               'paused': [('readonly', False)]},
        domain=[('colgap', '=', False)])
    original_move_line_ids = fields.One2many(
        'account.move.line', 'asset_id', string='Journal Items',
        readonly=True, states={'draft': [('readonly', False)]}, copy=False,
        domain=[('colgap', '=', False)])

    def _set_value(self):
        super(AccountAsesetColgap, self)._set_value()
        for record in self:
            if record.original_value_colgap == 0:
                record.original_value_colgap = record.original_value

    @api.onchange('account_asset_colgap_id')
    def _onchange_account_asset_colgap_id(self):
        self.display_model_choice = (
            self.state == 'draft' and len(self.env['account.asset'].search(
                [('state', '=', 'model'), (
                    'user_type_id', '=', self.user_type_id.id)])))
        if self.asset_type in ('purchase', 'expense'):
            self.account_depreciation_colgap_id = (
                self.account_depreciation_colgap_id or
                self.account_asset_colgap_id)
        else:
            self.account_depreciation_expense_colgap_id = (
                self.account_depreciation_expense_colgap_id or
                self.account_asset_colgap_id)

    @api.onchange('salvage_value_colgap')
    def _onchange_salvage_value_colgap(self):
        self.value_residual_colgap = (
            self.original_value_colgap - self.salvage_value_colgap)

    @api.depends('value_residual_colgap', 'salvage_value_colgap',
                 'children_ids.book_value_colgap')
    def _compute_book_value_colgap(self):
        for record in self:
            record.book_value_colgap = (
                record.value_residual_colgap + record.salvage_value_colgap +
                sum(record.children_ids.mapped('book_value_colgap')))
            record.gross_increase_value_colgap = sum(
                record.children_ids.mapped('original_value_colgap'))

    def _compute_board_amount_colgap(
            self,
            computation_sequence, residual_amount_colgap,
            amount_to_depreciate_colgap,
            depreciation_number_colgap,
            starting_sequence_colgap, depreciation_date):
        amount = 0
        if computation_sequence == depreciation_number_colgap:
            # last depreciation always takes the asset residual amount
            amount = residual_amount_colgap
        else:
            if self.method_colgap in ('degressive', 'degressive_then_linear'):
                amount = (
                    residual_amount_colgap *
                    self.method_progress_factor_colgap)
            if self.method_colgap in ('linear', 'degressive_then_linear'):
                nb_depreciation = (
                    depreciation_number_colgap - starting_sequence_colgap)
                if self.prorata:
                    nb_depreciation -= 1
                linear_amount = min(amount_to_depreciate_colgap /
                                    nb_depreciation, residual_amount_colgap)
                if self.method_colgap == 'degressive_then_linear':
                    amount = max(linear_amount, amount)
                else:
                    amount = linear_amount
        return amount

    def validation_credit_amount(self, debit, credit):
        account_depreciation_id = self.account_depreciation_colgap_id.id
        account_expense_id = self.account_depreciation_expense_colgap_id.id
        if credit > 0.0 and self.original_value_colgap > 0.0:
            return account_depreciation_id
        if debit > 0.0 and self.original_value_colgap > 0.0:
            return account_expense_id
        if credit > 0.0 and self.original_value_colgap < 0.0:
            return account_expense_id
        if debit > 0.0 and self.original_value_colgap < 0.0:
            return account_depreciation_id

    def _modifi_lines_move_colgap(self, move_val):
        move_val['colgap'] = True
        move_val['journal_id'] = self.journal_colgap_id.id
        for line in move_val.get('line_ids', []):
            vals_line = line[2]
            vals_line['account_id'] = self.validation_credit_amount(
                vals_line.get('debit', 0.0), vals_line.get('credit', 0.0))
        return move_val

    def _recompute_board_colgap(
            self, depreciation_number_colgap, starting_sequence_colgap,
            amount_to_depreciate_colgap, depreciation_date,
            already_depreciated_amount_colgap, amount_change_colgap_ids):
        self.ensure_one()
        residual_amount_colgap = amount_to_depreciate_colgap
        move_vals = []
        prorata = self.prorata and not self.env.context.get("ignore_prorata")
        if amount_to_depreciate_colgap != 0.0:
            for asset_sequence in range(
                    starting_sequence_colgap + 1,
                    depreciation_number_colgap + 1):
                while (amount_change_colgap_ids
                       and amount_change_colgap_ids[0].date
                       <= depreciation_date):
                    if not amount_change_colgap_ids[0].reversal_move_id:
                        residual_amount_colgap -= (
                            amount_change_colgap_ids[0].amount_total)
                        amount_to_depreciate_colgap -= (
                            amount_change_colgap_ids[0].amount_total)
                        already_depreciated_amount_colgap += (
                            amount_change_colgap_ids[0].amount_total)
                    amount_change_colgap_ids[0].write({
                        'asset_remaining_value': float_round(
                            residual_amount_colgap,
                            precision_rounding=self.currency_id.rounding),
                        'asset_depreciated_value': (
                            amount_to_depreciate_colgap -
                            residual_amount_colgap +
                            already_depreciated_amount_colgap),
                    })
                    amount_change_colgap_ids -= amount_change_colgap_ids[0]
                amount = self._compute_board_amount_colgap(
                    asset_sequence, residual_amount_colgap,
                    amount_to_depreciate_colgap, depreciation_number_colgap,
                    starting_sequence_colgap, depreciation_date)
                prorata_factor = 1
                move_ref = (
                    self.name + ' (%s/%s)' % (prorata and asset_sequence - 1
                                              or asset_sequence,
                                              self.method_number_colgap))
                if prorata and asset_sequence == 1:
                    move_ref = self.name + ' ' + _('(prorata entry)')
                    first_date = self.prorata_date
                    if int(self.method_period_colgap) % 12 != 0:
                        month_days = (
                            calendar.monthrange(
                                first_date.year, first_date.month)[1])
                        days = month_days - first_date.day + 1
                        prorata_factor = days / month_days
                    else:
                        total_days = ((depreciation_date.year %
                                       4) and 365 or 366)
                        days = ((
                            self.company_id.compute_fiscalyear_dates(
                                first_date)['date_to'] - first_date).days + 1)
                        prorata_factor = days / total_days
                amount = self.currency_id.round(amount * prorata_factor)
                if float_is_zero(amount,
                                 precision_rounding=self.currency_id.rounding):
                    continue
                residual_amount_colgap -= amount
                move_val = self.env[
                    'account.move'].with_context(
                    colgap=True
                )._prepare_move_for_asset_depreciation(
                        {
                            'amount': amount,
                            'asset_id': self,
                            'move_ref': move_ref,
                            'date': depreciation_date,
                            'asset_remaining_value': (
                                float_round(
                                    residual_amount_colgap,
                                    precision_rounding=(
                                        self.currency_id.rounding))),
                            'asset_depreciated_value': (
                                amount_to_depreciate_colgap -
                                residual_amount_colgap +
                                already_depreciated_amount_colgap),
                            'colgap': True
                        })
                move_val = self._modifi_lines_move_colgap(move_val)
                move_vals.append(move_val)
                depreciation_date = (
                    depreciation_date + relativedelta(
                        months=+int(self.method_period_colgap)))
                # datetime doesn't take into account that the number of
                # days is not the same for each month
                if int(self.method_period_colgap) % 12 != 0:
                    max_day_in_month = calendar.monthrange(
                        depreciation_date.year, depreciation_date.month)[1]
                    depreciation_date = depreciation_date.replace(
                        day=max_day_in_month)
        return move_vals

    def compute_depreciation_board_colgap(self):
        amount_change_colgap_ids = (
            self.depreciation_move_colgap_ids.filtered(
                lambda x: x.asset_value_change and
                not x.reversal_move_id).sorted(key=lambda l: l.date))
        posted_depreciation_move_colgap_ids = (
            self.depreciation_move_colgap_ids.filtered(
                lambda x: x.state == 'posted' and not x.asset_value_change
                and not x.reversal_move_id).sorted(key=lambda l: l.date))
        already_depreciated_amount_colgap = sum(
            [m.amount_total for m in
             posted_depreciation_move_colgap_ids])
        depreciation_number_colgap = self.method_number_colgap
        if self.prorata:
            depreciation_number_colgap += 1
        starting_sequence_colgap = 0
        amount_to_depreciate_colgap = (
            self.value_residual_colgap + sum(
                [m.amount_total for m in amount_change_colgap_ids]))
        depreciation_date = self.first_depreciation_date
        if (posted_depreciation_move_colgap_ids and
                posted_depreciation_move_colgap_ids[-1].date):
            last_depreciation_date_colgap = (
                fields.Date.from_string(
                    posted_depreciation_move_colgap_ids[-1].date))
            if last_depreciation_date_colgap > depreciation_date:
                depreciation_date = (
                    last_depreciation_date_colgap +
                    relativedelta(months=+int(self.method_period_colgap)))
        commands = [
            (2, line_id.id, False) for line_id in
            self.depreciation_move_colgap_ids.filtered(
                lambda x: x.state == 'draft')]
        new_lines_colgap = self._recompute_board_colgap(
            depreciation_number_colgap, starting_sequence_colgap,
            amount_to_depreciate_colgap, depreciation_date,
            already_depreciated_amount_colgap, amount_change_colgap_ids)
        new_line_vals_list = []
        for new_line_vals in new_lines_colgap:
            # no need of amount field, as it is computed and we don't
            # want to trigger its inverse function
            del(new_line_vals['amount_total'])
            new_line_vals_list.append(new_line_vals)
        new_moves_colgap = self.env['account.move'].create(new_line_vals_list)
        for move in new_moves_colgap:
            commands.append((4, move.id))
        return self.write({'depreciation_move_colgap_ids': commands})

    def compute_depreciation_board(self):
        result = super(AccountAsesetColgap, self).compute_depreciation_board()
        self.compute_depreciation_board_colgap()
        return result

    def validate(self):
        fields = [
            'method',
            'method_colgap',
            'method_number',
            'method_number_colgap',
            'method_period',
            'method_period_colgap',
            'method_progress_factor',
            'method_progress_factor_colgap',
            'salvage_value',
            'salvage_value_colgap',
            'original_move_line_ids',
            'original_move_line_colgap_ids'
        ]
        ref_tracked_fields = self.env['account.asset'].fields_get(fields)
        self.write({'state': 'open'})
        for asset in self:
            tracked_fields = ref_tracked_fields.copy()
            if asset.method == 'linear':
                del(tracked_fields['method_progress_factor'])
            if asset.method_colgap == 'linear':
                del(tracked_fields['method_progress_factor_colgap'])
            dummy, tracking_value_ids = asset._message_track(
                tracked_fields, dict.fromkeys(fields))
            asset_name = {
                'purchase': (
                    _('Asset created'),
                    _('An asset has been created for this move:')),
                'sale': (
                    _('Deferred revenue created'),
                    _('A deferred revenue has been created for this move:')),
                'expense': (
                    _('Deferred expense created'),
                    _('A deferred expense has been created for this move:')),
            }[asset.asset_type]
            msg = (
                asset_name[1] +
                ' <a href=# data-oe-model=account.asset data-oe-id=%d>%s</a>'
                % (asset.id, asset.name))
            asset.message_post(
                body=asset_name[0], tracking_value_ids=tracking_value_ids)
            for move_id in asset.original_move_line_ids.mapped('move_id'):
                move_id.message_post(body=msg)
            if (not asset.depreciation_move_ids and
                    not asset.depreciation_move_colgap_ids):
                asset.compute_depreciation_board()
                asset.compute_depreciation_board_colgap()
            asset._check_depreciations()
            asset.depreciation_move_ids.write({'auto_post': True})

    @api.onchange('original_value_colgap')
    def _compute_fields_colgap(self):
        for record in self:
            record.value_residual_colgap = (
                record.original_value_colgap - record.salvage_value_colgap)
