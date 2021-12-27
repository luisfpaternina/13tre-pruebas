# coding: utf-8

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    @api.depends(
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state')
    def _compute_amount(self):
        invoices = self.filtered(lambda x: x.is_sale_document())
        for invoice in invoices:
            invoice.amount_discount = abs(sum(
                (line.quantity * line.price_unit * line.discount) / 100
                for line in invoice.invoice_line_ids if line.discount > 0
            )) or 0.00
            invoice.amount_surchange = abs(sum(
                (line.quantity * line.price_unit * line.discount) / 100
                for line in invoice.invoice_line_ids if line.discount < 0
            )) or 0.00
            invoice.total_without_sur_disc = abs(sum(
                (line.quantity * line.price_unit)
                for line in invoice.invoice_line_ids
            )) or 0.00
        super(AccountInvoice, self)._compute_amount()

    total_without_sur_disc = fields.Monetary(
        string='Free Amount',
        store=True,
        readonly=True,
        compute='_compute_amount',
        track_visibility='always'
    )

    sur_disc_type_id = fields.Many2one(
        'surchange.discount.type',
        string="Surcharge/Discount Type",
    )

    discount_type = fields.Selection([
        ('none', 'Not Apply'),
        ('percent', 'Percentage'),
        ('amount', 'Amount')],
        string='Discount Type',
        readonly=True,
        states={'draft': [('readonly', False)]},
        default='none'
    )
    discount_rate = fields.Float(
        'Discount Amount',
        digits='Discount',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    amount_discount = fields.Monetary(
        string='Discount',
        store=True,
        readonly=True,
        compute='_compute_amount',
        track_visibility='always'
    )

    amount_surchange = fields.Monetary(
        string='Surcharge',
        store=True,
        readonly=True,
        compute='_compute_amount',
        track_visibility='always'
    )

    apply_global_discount = fields.Boolean(
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    @api.onchange('discount_type', 'discount_rate')
    def onchange_discount_type_rate(self):
        for inv in self:
            inv.apply_global_discount = False

    @api.onchange('apply_global_discount')
    def supply_rate(self):
        for inv in self:
            if not inv.apply_global_discount:
                continue
            if inv.discount_type == 'percent' and inv.discount_rate > 100:
                return {
                    'warning': {
                        'title': _('Discount Rate Error'),
                        'message': _('The global percentage is greater '
                                     'than one hundred')
                    },
                }
            if inv.discount_type == 'percent':
                for line in inv.line_ids:
                    total = (line.quantity * line.price_unit)
                    line.discount = inv.discount_rate
                    line.discount_amount = (total * line.discount) / 100
                    line._onchange_price_subtotal()
            else:
                total = discount = 0.0
                for line in inv.invoice_line_ids:
                    total += (line.quantity * line.price_unit)
                discount = ((inv.discount_rate / total) * 100
                            if inv.discount_rate != 0 else inv.discount_rate)
                for line in inv.line_ids:
                    line.discount = discount
                    line.discount_amount = (total * line.discount) / 100
                    line._onchange_price_subtotal()
            inv._compute_invoice_taxes_by_group()
            inv._onchange_invoice_line_ids()

    @api.onchange('invoice_line_ids')
    def _onchange_invoice_line_ids(self):
        for inv in self:
            total_discount = 0
            total_surchange = 0
            for line in inv.invoice_line_ids:
                total = (line.quantity * line.price_unit)
                if not line.apply_discount or total == 0:
                    continue
                line.discount = (line.discount_amount / total) * 100
                line._onchange_price_subtotal()
                total_discount += ((total * line.discount) / 100 if
                                   line.discount > 0 else 0)
                total_surchange += ((total * line.discount) / 100 if
                                    line.discount < 0 else 0)
                line.discount_amount = (total * line.discount) / 100
                line.apply_discount = False

            inv.amount_discount += total_discount
            inv.amount_surchange += total_surchange
            inv.apply_global_discount = False
            inv.discount_rate = 0
            inv.discount_type = 'none'
            inv._compute_invoice_taxes_by_group()
        super(AccountInvoice, self)._onchange_invoice_line_ids()

    def _get_surchange_discount_data(self):
        result = []
        lines = self.invoice_line_ids.filtered(
            lambda line: line.discount != 0.0)
        for line in lines:
            total = (line.quantity * line.price_unit)
            if total == 0:
                continue
            discount = (line.discount_amount / total) * 100
            _type = 'discount' if line.discount > 0 else 'surchange'
            discount_amount = (total * line.discount) / 100
            result.append({
                'type': _type,
                'rate': discount,
                'amount': discount_amount,
                'total': total,
            })

        return result


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    discount_amount = fields.Float(
        string='Disc Tot',
        digits='Discount',
        default=0.0,
        store=False,
    )

    discount = fields.Float(
        string='Discount (%)',
        digits='Discount',
        default=0.0
    )

    apply_discount = fields.Boolean()

    def _get_surchange_discount_by_line(self):
        result = []
        total = (self.quantity * self.price_unit)
        if total == 0:
            return result
        _type = 'discount' if self.discount > 0 else 'surchange'
        discount = 'false' if self.discount > 0 else 'true'
        discount_amount = (total * self.discount) / 100
        result.append({
            'type': _type,
            'discount': discount,
            'rate': self.discount,
            'amount': discount_amount,
            'total': total,
        })
        return result
