# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from datetime import date
import math


class Credit(models.Model):
    _name = 'credit'

    name = fields.Char(
        compute="asign_name",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    res_partner_id = fields.Many2one(
        'res.partner',
        required=True,
        string="Client"
    )
    credit_type_id = fields.Many2one(
        'credit.type',
        index=True,
        required=True
    )
    modality = fields.Selection(
        [
            ('revolving', 'Revolving'),
            ('amortized', 'Amortized')
        ],
        index=True,
        required=True
    )
    number_credit = fields.Float(
        required=True,
        digits=(17, 0)
    )
    credit_limit = fields.Float(
        string="Base Value of Credit",
        required=True
    )
    available_balance = fields.Float()
    state = fields.Selection(
        [
            ('active', 'Active'),
            ('in_debt', 'In Debt'),
            ('paid_out', 'Paid out')
        ],
        index=True,
        default="active"
    )
    sponsoring_entity_id = fields.Many2one(
        'res.bank',
        index=True,
        required=True
    )

    term_months = fields.Integer()
    credit_value_accounted = fields.Float()
    endorsement_commission = fields.Float()
    endorsement_value_plus_vat = fields.Float()
    disbursement_date = fields.Date()
    credit_lines = fields.One2many(
        'credit.line', 'credit_id', string="Credit Lines"
    )
    client_type = fields.Selection(
        [
            ('natural', 'Natural person'),
            ('legal', 'Legal person')
        ],
        default='natural',
        required=True
    )
    invoice_number = fields.Char(
        string = "Invoice Number",
    )

    @api.onchange('res_partner_id', 'number_credit')
    def asign_name(self):
        for rc in self:
            if rc.res_partner_id:
                rc.name = (
                    f'{rc.res_partner_id.name} - '
                    f'{int(rc.number_credit)}'
                )

    @api.onchange('credit_type_id')
    def _onchange_credit_type_id(self):
        return {
            'domain': {
                'sponsoring_entity_id': [
                    (
                        'id', 'in', self.mapped(
                            'credit_type_id.supporting_entity_ids.id'
                        )
                    )
                ]
            }
        }

    @api.onchange('endorsement_commission', 'credit_limit')
    def _calculate_endorsement_value_plus_vat(self):
        self.ensure_one()
        percentage_endorsement_commission = (
            (self.credit_limit * self.endorsement_commission) / 100
        )
        self.endorsement_value_plus_vat = (
            percentage_endorsement_commission +
            ((percentage_endorsement_commission) * 0.19)
        )

    @api.onchange('credit_limit', 'endorsement_value_plus_vat')
    def _calculate_credit_value_accounted(self):
        self.ensure_one()
        self.credit_value_accounted = (
            self.credit_limit + self.endorsement_value_plus_vat
        )

    def verify_fields_for_calculate_payment_schedule(self):
        self.ensure_one()
        if (
            not self.disbursement_date or
            not self.term_months or
            not self.credit_limit or
            not self.credit_value_accounted
        ):
            raise ValidationError(
                _(
                    "It is necessary to fill in the following fields:"
                    "\n(disbursement_date, term_months, base_value_credit"
                    ", credit_value_accounted)"
                )
            )

    def calculate_payment_schedule(self):
        self.ensure_one()
        old_credit_lines = self.env['credit.line'].search(
            [('credit_id', '=', self.id)]
        )
        old_credit_lines.unlink()
        self.verify_fields_for_calculate_payment_schedule()
        payment_date = self.disbursement_date
        balance = self.credit_value_accounted
        payment_capital = math.ceil(self.credit_limit/self.term_months)
        interest = math.ceil(self.endorsement_value_plus_vat/self.term_months)
        quota = payment_capital + interest
        for i in range(1, self.term_months + 1):
            payment_date += relativedelta(months=1)
            balance -= payment_capital
            self.env['credit.line'].create(
                {
                    'credit_id': self.id,
                    'payment_date': payment_date,
                    'installment_number': i,
                    'capital_subscription': payment_capital,
                    'bank_interest': interest,
                    'amount_to_be_paid': quota,
                    'capital_balance': balance
                }
            )
        # Create receipts for each credit line
        self.create_lines_receipts()

    # Create receipts for each credit line
    def create_lines_receipts(self):
        self.ensure_one()
        for line in self.credit_lines:
            line.create_receipt()

    # Update notes in each line's receipt
    @api.onchange('credit_type_id', 'number_credit', 'invoice_number')
    def _update_receipts_notes(self):
        self.ensure_one()
        for line in self.credit_lines:
            if line.receipt_id:
                if self.invoice_number:
                    receipt_notes = _("""Credit Data:
                        Invoice Number: %s
                        Credit type: %s
                        Credit Number: %s\n""") % (
                            self.invoice_number, 
                            self.credit_type_id.name,
                            self.number_credit,
                        )
                else:
                    receipt_notes = _("""Credit Data:
                        Credit type: %s
                        Credit Number: %s\n""") % (
                            self.credit_type_id.name,
                            self.number_credit,
                        )
                line.receipt_id.write({
                    'narration': receipt_notes,
                    'ref': self.invoice_number or '',
                })

    # Publish receipts related with the credit
    def publish_receipts(self):
        self.ensure_one()
        for line in self.credit_lines:
            if line.receipt_id:
                line.receipt_id.action_post()

    def check_credit_line_status(self):
        credit_ids = self.env['credit'].search([
            ('state', 'in', ['active', 'in_debt'])
        ])
        for credit in credit_ids:
            credit_paid = True
            credit_in_debt = False
            for line in credit.credit_lines:
                if line.receipt_id:
                    if line.receipt_id.amount_residual:
                        credit_paid = False
                        if line.receipt_id.invoice_date_due < date.today():
                            credit_in_debt = True
                else:
                    credit_paid = False
                    
            if credit_paid:
                credit.state = 'paid_out'
            elif credit_in_debt:
                credit.state = 'in_debt'
            else:
                credit.state = 'active'

    def unlink(self):
        for record in self:
            lines = record.credit_lines
            published_receipts = [
                x.receipt_id for x in lines if x.receipt_id.state == 'posted'
            ]
            if published_receipts:
                raise ValidationError(
                    _("You can't delete credits with receipts published.")
                )
            for line in lines:
                models.Model.unlink(line)
        return models.Model.unlink(self)


class CreditLine(models.Model):
    _name = 'credit.line'

    name = fields.Char(
        compute="_asign_name",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )

    credit_id = fields.Many2one(
        'credit',
        readonly=True
    )
    company_currency_id = fields.Many2one(
        'res.currency',
        string='Company Currency',
        readonly=True,
        default=lambda self: self.env.company.currency_id
    )
    payment_date = fields.Date()
    installment_number = fields.Integer()
    capital_subscription = fields.Monetary(
        currency_field='company_currency_id'
    )
    bank_interest = fields.Monetary(currency_field='company_currency_id')
    amount_to_be_paid = fields.Monetary(currency_field='company_currency_id')
    capital_balance = fields.Monetary(currency_field='company_currency_id')
    receipt_id = fields.Many2one(
        comodel_name='account.move',
        string="Receipt",
    )

    # Unlink receipt related
    def unlink(self):
        if self.receipt_id:
            self.receipt_id.unlink()
        return super(CreditLine, self).unlink()

    @api.onchange('credit_id', 'installment_number')
    def _asign_name(self):
        for record in self:
            if record.credit_id and record.installment_number:
                record.name = (
                    f'{record.installment_number} - '
                    f'{record.credit_id.name}'
                )

    # Create receipts to record pays 
    def create_receipt(self):
        self.ensure_one()
        if self.credit_id.invoice_number:
            receipt_notes = _("""Credit Data:
                Invoice Number: %s
                Credit type: %s
                Credit Number: %s\n""") % (
                    self.credit_id.invoice_number, 
                    self.credit_id.credit_type_id.name,
                    self.credit_id.number_credit,
                )
        else:
            receipt_notes = _("""Credit Data:
                Credit type: %s
                Credit Number: %s\n""") % (
                    self.credit_id.credit_type_id.name,
                    self.credit_id.number_credit,
                )

        product = self.env.ref(
            'allocation_of_credit_amount.payment_of_credits_product'
        )
        dairy_ref = self.env.ref(
            'allocation_of_credit_amount.payment_of_credits_dairy'
        )

        # Customer assignment
        assigned_partner = self.credit_id.res_partner_id \
            if self.credit_id.credit_type_id.receivable != 'bank'\
                else self.credit_id.sponsoring_entity_id.partner_id

        print('\n\n\n\n\n\n\n\n')
        print(assigned_partner.name )
        print('\n\n\n\n\n\n\n\n')

        receipt_vals = {
            'invoice_date': date.today(),
            'invoice_date_due': self.payment_date,
            'partner_id': assigned_partner,
            'type': 'out_receipt',
            'ref': self.credit_id.invoice_number,
            'journal_id': dairy_ref.id,
            'narration': receipt_notes,
            'company_id': self.env.company.id
        }
        receipt = self.env['account.move'].create(receipt_vals)

        receipt_lines_vals = {
            'product_id': product.id,
            'price_unit': self.amount_to_be_paid,
            'account_id': dairy_ref.default_debit_account_id.id,
            'quantity': 1,
            'price_subtotal': self.amount_to_be_paid,
            'exclude_from_invoice_tab': False,
        }

        receipt.write({
            'invoice_line_ids': [(0,0, receipt_lines_vals)],
            'credit_line_id': self.id,
        })

        receipt_line = receipt.invoice_line_ids[0]
        self.receipt_id = receipt.id
