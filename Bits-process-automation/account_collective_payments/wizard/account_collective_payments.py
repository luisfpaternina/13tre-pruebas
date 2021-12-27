# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountCollectivePayments(models.TransientModel):
    _name = 'account.collective.payments.wizard'

    _description = ''

    def _domain_payment_method(self):
        return [('payment_type', '=', 'outbound')]

    def _default_electronic_method(self):
        payment_method = self.env['account.payment.method'].search([
            ('payment_type', '=', 'outbound'),
            ('code', '=', 'electronic_out')], limit=1)
        return payment_method.id

    name = fields.Char(string="Document")

    payment_type = fields.Selection([
        ('outbound', 'Send Money'),
        ('inbound', 'Receive Money')],
        string='Payment Type',
        required=True, default='outbound')
    payment_method_id = fields.Many2one(
        'account.payment.method',
        string='Payment Method',
        required=True, domain=_domain_payment_method,
        default=_default_electronic_method)
    date = fields.Date(
        default=fields.Date.context_today,
        required=True)
    amount = fields.Monetary(compute="_compute_amount_payment", store=True)
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        default=lambda self: self.env.company.currency_id)
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        required=True, domain=[('type', '=', 'bank')])
    company_id = fields.Many2one('res.company',
                                 related='journal_id.company_id',
                                 string='Company', readonly=True)
    account_id = fields.Many2one(
        'account.account')
    date_from_f = fields.Date(
        string='Date from',
        required=True,
        default=datetime.now().strftime('%Y-%m-01'))
    date_to_f = fields.Date(
        string='Date to',
        required=True,
        default=str(datetime.now() + relativedelta(
            months=+1, day=1, days=-1))[:10])
    journal_id_f = fields.Many2one(
        'account.journal',
        string='Journal to pay')
    account_id_f = fields.Many2one(
        'account.account',
        string='Accounting Account')
    partner_id_f = fields.Many2one(
        'res.partner',
        string='Partner')

    line_ids = fields.Many2many(
        'account.move.line',
        string='Journal Items')

    clean_lines = fields.Boolean(
        default=False
    )

    bank_id = fields.Many2one('res.bank', string='Bank')

    journal_type_f = fields.Selection([
        ('sale', 'Sales'),
        ('purchase', 'Purchase'),
        ('cash', 'Cash'),
        ('bank', 'Bank'),
        ('general', 'Miscellaneous'),
    ], string='Journal Type')

    group_apply = fields.Boolean(
        default=False,
        string='Group by partner and account'
    )
    create_line_bank = fields.Boolean(
        string="Create Bank Line by Movement",
        default=False
    )

    def _check_dates(self, date_start, date_end):
        self.ensure_one()
        start = date_start or False
        end = date_end or False
        if start and end and date_end >= date_start:
            return False
        return True

    @api.onchange('journal_type_f')
    def _onchange_process_type(self):
        if self.journal_type_f:
            return {
                'domain': {
                    'journal_id_f': [('type', '=', self.journal_type_f)]
                }
            }
        return {'domain': {'journal_id_f': []}}

    @api.onchange('journal_id_f')
    def _onchange_journal_id_f(self):
        domain = []
        if self.journal_id_f and self.journal_id_f.account_control_ids:
            domain += [('id', 'in', self.journal_id_f.account_control_ids.ids)]
        return {'domain': {'account_id_f': domain}}

    @api.onchange(
        'date_from_f',
        'date_to_f',
        'journal_id_f',
        'account_id_f',
        'partner_id_f',
        'bank_id')
    def _onchange_line_list(self):
        if self._check_dates(self.date_from_f, self.date_to_f):
            self.date_from_f = False
            return {
                'warning': {
                    'title': _('Error'),
                    'message': _('The start date must be less than end date'),
                }
            }

        domain = [
            ('parent_state', '=', 'posted'),
            ('reconciled', '=', False),
            ('date', '>=', self.date_from_f),
            ('date', '<=', self.date_to_f),
            ('credit', '>', 0),
        ]

        if self.journal_type_f:
            domain += [('journal_id.type', '=', self.journal_type_f)]
        if self.journal_id_f:
            domain += [('journal_id', '=', self.journal_id_f.id)]
        if self.account_id_f:
            domain += [('account_id', '=', self.account_id_f.id)]
        if self.partner_id_f:
            domain += [('partner_id', '=', self.partner_id_f.id)]
        if self.bank_id:
            domain += [('partner_id.bank_ids.bank_id', '=', self.bank_id.id)]

        return {'domain': {'line_ids': domain}}

    @api.onchange('clean_lines')
    def _onchange_line_ids(self):
        if self.clean_lines:
            self.line_ids = False
            self.clean_lines = False

    @api.depends('line_ids')
    def _compute_amount_payment(self):
        for record in self:
            line_amount_sum = 0.0
            for line in record.line_ids:
                line_amount_sum += abs(line.amount_residual)
            record.amount = line_amount_sum

    def _get_collective_payment_vals(self):
        partner_type = ("supplier" if self.payment_type == 'outbound'
                        else "customer")

        values = {
            'journal_id': self.journal_id.id,
            'payment_method_id': self.payment_method_id.id,
            'payment_date': self.date,
            'communication': " ",
            'payment_type': self.payment_type,
            'amount': abs(self.amount),
            'currency_id': self.company_id.currency_id.id,
            'partner_id': self.company_id.partner_id.id,
            'partner_type': partner_type,
            'state': "draft"
        }
        return values

    def _get_currency_payment(self, payment_id, counterpart_amount,
                              write_off_amount):
        company_currency = payment_id.company_id.currency_id
        # Single-currency.
        currency_id = False
        balance = counterpart_amount
        write_off_balance = write_off_amount
        counterpart_amount = write_off_amount = 0.0
        # Manage currency.
        if payment_id.currency_id != company_currency:
            # Multi-currencies.
            balance = payment_id.currency_id._convert(
                counterpart_amount, company_currency, payment_id.company_id,
                payment_id.payment_date)
            write_off_balance = payment_id.currency_id._convert(
                write_off_amount, company_currency, payment_id.company_id,
                payment_id.payment_date)
            currency_id = payment_id.currency_id.id
        return currency_id, balance, company_currency

    def _get_liquidity_account(self, journal_id, amount):
        counterpart_amount = amount
        liquidity_line_account = (
            journal_id.default_debit_account_id)
        return liquidity_line_account, counterpart_amount

    def _get_liquidity_account_currency(self, payment_id,
                                        company_currency, balance,
                                        currency_id, counterpart_amount):
        liquidity_line_currency_id = currency_id
        liquidity_amount = counterpart_amount
        if (payment_id.journal_id.currency_id
                and payment_id.currency_id !=
                payment_id.journal_id.currency_id):
            # Custom currency on journal.
            # Single-currency
            liquidity_line_currency_id = False
            if payment_id.journal_id.currency_id == company_currency:
                liquidity_line_currency_id = (
                    payment_id.journal_id.currency_id.id)
                liquidity_amount = company_currency._convert(
                    balance, payment_id.journal_id.currency_id,
                    payment_id.company_id, payment_id.payment_date)
        return liquidity_amount, liquidity_line_currency_id

    def _get_format_group_vals(self):
        list_lines = self.line_ids.read([
            'name', 'partner_id', 'account_id', 'amount_residual'])
        dict_payslip_lines = {}
        for line in list_lines:
            index = str(line['partner_id'][0]) + '_' + \
                str(line['account_id'][0])
            if not dict_payslip_lines.get(index, False):
                dict_payslip_lines[index] = line.copy()
                dict_payslip_lines[index]['amount_residual'] = 0
                dict_payslip_lines[index]['ids'] = []
            dict_payslip_lines[index]['amount_residual'] +=\
                line['amount_residual']
            dict_payslip_lines[index]['ids'].append(line['id'])
        return dict_payslip_lines

    def _get_format_group_move_line_vals(self, payment_id, currency_id):
        vals_lines = []
        dict_payslip_lines = self._get_format_group_vals()
        for line in dict_payslip_lines.values():
            credit = 0.0
            debit = abs(line['amount_residual'])
            vals_lines.append(
                (0, 0, {
                    'name': line['name'],
                    'partner_id': line['partner_id'][0],
                    'account_id': line['account_id'][0],
                    'payment_id': payment_id.id,
                    'date_maturity': payment_id.payment_date,
                    'debit': debit,
                    'credit': credit,
                    'currency_id': currency_id
                })
            )

        return vals_lines

    def _get_format_move_line_vals(self, payment_id, currency_id):
        vals_lines = []
        for line in self.line_ids:
            credit = 0.0
            debit = abs(line.amount_residual)
            vals_lines.append(
                (0, 0, {
                    'name': line.name,
                    'partner_id': line.partner_id.id,
                    'account_id': line.account_id.id,
                    'payment_id': payment_id.id,
                    'date_maturity': payment_id.payment_date,
                    'debit': debit,
                    'credit': credit,
                    'currency_id': currency_id
                })
            )
        return vals_lines

    def _get_general_liquidity_line(self, payment_id, liquidity_amount,
                                    liquidity_line_currency_id, balance,
                                    liquidity_line_account):
        vals_lines = [(0, 0, {
            'name': payment_id.name or _("Line Bank"),
            'amount_currency': (-liquidity_amount
                                if liquidity_line_currency_id else 0.0),
            'currency_id': liquidity_line_currency_id,
            'debit': balance < 0.0 and -balance or 0.0,
            'credit': balance > 0.0 and balance or 0.0,
            'date_maturity': payment_id.payment_date,
            'partner_id': payment_id.partner_id.commercial_partner_id.id,
            'account_id': liquidity_line_account.id,
            'payment_id': payment_id.id,
        })]
        return vals_lines

    def _get_devided_general_liquidity_line(self, payment_id,
                                            write_off_amount):
        vals_lines = []
        for line in self.line_ids:
            amount = line.amount_residual
            liquidity_line_account, amount = (
                self._get_liquidity_account(payment_id.journal_id,
                                            amount))
            currency_id, balance, company_currency = (
                self._get_currency_payment(payment_id, amount,
                                           write_off_amount))
            liquidity_amount, liquidity_line_currency_id = (
                self._get_liquidity_account_currency(
                    payment_id, company_currency, balance, currency_id,
                    amount))
            vals_lines.append(
                (0, 0, {
                    'name': payment_id.name or _("Line Bank"),
                    'amount_currency': (-liquidity_amount
                                        if liquidity_line_currency_id
                                        else 0.0),
                    'currency_id': currency_id,
                    'debit': balance > 0.0 and balance or 0.0,
                    'credit': balance < 0.0 and -balance or 0.0,
                    'date_maturity': payment_id.payment_date,
                    'partner_id': line.partner_id.id,
                    'account_id': liquidity_line_account.id,
                    'payment_id': payment_id.id,
                })
            )
        return vals_lines

    def _get_devided_group_liquidity_line(self, payment_id, write_off_amount):
        vals_lines = []
        dict_payslip_lines = self._get_format_group_vals()
        for line in dict_payslip_lines.values():
            amount = line['amount_residual']
            liquidity_line_account, amount = (
                self._get_liquidity_account(payment_id.journal_id,
                                            amount))
            currency_id, balance, company_currency = (
                self._get_currency_payment(payment_id, amount,
                                           write_off_amount))
            liquidity_amount, liquidity_line_currency_id = (
                self._get_liquidity_account_currency(
                    payment_id, company_currency, balance, currency_id,
                    amount))
            vals_lines.append(
                (0, 0, {
                    'name': payment_id.name or _("Line Bank"),
                    'amount_currency': (-liquidity_amount
                                        if liquidity_line_currency_id
                                        else 0.0),
                    'currency_id': currency_id,
                    'debit': balance > 0.0 and balance or 0.0,
                    'credit': balance < 0.0 and -balance or 0.0,
                    'date_maturity': payment_id.payment_date,
                    'partner_id': line['partner_id'][0],
                    'account_id': liquidity_line_account.id,
                    'payment_id': payment_id.id,
                })
            )

        return vals_lines

    def _get_divided_liquidity_line(self, payment_id, currency_id,
                                    write_off_amount):
        vals_lines = (self._get_devided_group_liquidity_line(
            payment_id, write_off_amount) if self.group_apply
            else self._get_devided_general_liquidity_line(
                payment_id, write_off_amount))
        return vals_lines

    def _get_move_line_vals(self, payment_id):
        vals_lines = []
        liquidity_line_account, counterpart_amount = (
            self._get_liquidity_account(payment_id.journal_id,
                                        payment_id.amount))
        write_off_amount = (
            payment_id.payment_difference_handling == 'reconcile'
            and -payment_id.payment_difference or 0.0)
        currency_id, balance, company_currency = (
            self._get_currency_payment(payment_id, counterpart_amount,
                                       write_off_amount))
        liquidity_amount, liquidity_line_currency_id = (
            self._get_liquidity_account_currency(
                payment_id, company_currency, balance, currency_id,
                counterpart_amount))

        vals_lines += (self._get_format_group_move_line_vals(
            payment_id, currency_id) if self.group_apply
            else self._get_format_move_line_vals(payment_id, currency_id))

        vals_lines += (self._get_divided_liquidity_line(
            payment_id, liquidity_line_currency_id, write_off_amount)
            if self.create_line_bank else self._get_general_liquidity_line(
            payment_id, liquidity_amount, liquidity_line_currency_id, balance,
            liquidity_line_account))

        return vals_lines

    def _get_move_vals(self, payment_id):
        move_vals = {
            'date': payment_id.payment_date,
            'ref': payment_id.communication,
            'journal_id': payment_id.journal_id.id,
            'currency_id': (payment_id.journal_id.currency_id.id or
                            payment_id.company_id.currency_id.id),
            'partner_id': payment_id.company_id.partner_id.id,
            'line_ids': self._get_move_line_vals(payment_id)
        }
        return move_vals

    def _generate_journal_entry(self, payment_id):
        AccountMove = self.env['account.move'].with_context(
            default_type='entry')
        # keep the name in case of a payment reset to draft
        if not payment_id.name:
            # Use the right sequence to set the name
            # if payment_id.partner_type == 'customer':
            #     if payment_id.payment_type == 'inbound':
            #         sequence_code = 'account.payment.customer.invoice'
            #     if payment_id.payment_type == 'outbound':
            #         sequence_code = 'account.payment.customer.refund'
            # if payment_id.partner_type == 'supplier':
            # if payment_id.payment_type == 'inbound':
            #     sequence_code = 'account.payment.supplier.refund'
            # if payment_id.payment_type == 'outbound':
            sequence_code = 'account.payment.supplier.invoice'
            payment_id.name = self.env['ir.sequence'].next_by_code(
                sequence_code, sequence_date=payment_id.payment_date)
            if not payment_id.name and payment_id.payment_type != 'transfer':
                raise UserError(
                    _("You have to define a sequence "
                      "for % s in your company.") % (sequence_code,))
        move = AccountMove.create(self._get_move_vals(payment_id))
        move.post()

    def reconcile_process(self, payment_id):
        if not self.group_apply:
            lines = self.env['account.move.line'].browse(self.line_ids.ids)
            for move in lines:
                re_move = self.search_counterpart_move(
                    payment_id, move.account_id.id,
                    move.credit, move.partner_id.id)
                (move + re_move).reconcile()
                continue
            return
        dict_lines = self._get_format_group_vals()
        for move in dict_lines.values():
            re_move = self.search_counterpart_move(
                payment_id, move['account_id'][0],
                abs(move['amount_residual']), move['partner_id'][0])
            move_ids = self.env['account.move.line'].browse(move['ids'])
            (move_ids + re_move).reconcile()

    def search_counterpart_move(self, payment_id, account_id,
                                debit, partner_id):
        limit = 1 if not self.group_apply else None
        return self.env['account.move.line'].search([
            ('payment_id', '=', payment_id.id),
            ('account_id', '=', account_id),
            ('partner_id', '=', partner_id),
            ('reconciled', '=', False),
            ('debit', '=', debit)], order='id desc', limit=limit)

    def generate_payments_action(self):
        payment = self.env['account.payment']
        for record in self:
            payment_vals = record._get_collective_payment_vals()
            payment_id = payment.create(payment_vals)
            self._generate_journal_entry(payment_id)

            record.reconcile_process(payment_id)
            payment_id.state = 'posted'

            return {
                'name': _('Payment'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.payment',
                'domain': [('id', 'in', [payment_id.id])]
            }
