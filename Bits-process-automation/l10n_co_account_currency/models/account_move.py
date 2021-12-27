# coding: utf-8

from odoo.tools.misc import formatLang, format_date, get_lang
from datetime import date
from datetime import datetime, timedelta
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    show_other_currency = fields.Boolean(
        compute="_compute_is_show_other_currency",
        default=False,
    )

    local_total_unsurdisc = fields.Monetary(
        string='Free Amount',
        currency_field='company_currency_id',
        store=True,
        readonly=True,
        compute='_compute_amount',
    )

    local_amount_discount = fields.Monetary(
        string='Discount',
        currency_field='company_currency_id',
        store=True,
        readonly=True,
        compute='_compute_amount',
    )
    local_amount_surchange = fields.Monetary(
        string='Surchange',
        currency_field='company_currency_id',
        store=True,
        readonly=True,
        compute='_compute_amount',
    )
    local_amount_untaxed = fields.Monetary(
        string='Amount Untaxed',
        currency_field='company_currency_id',
        store=True,
        readonly=True,
        compute='_compute_amount',
    )
    local_amount_total = fields.Monetary(
        string='Total',
        currency_field='company_currency_id',
        store=True,
        readonly=True,
        compute='_compute_amount',
    )

    local_amount_by_group = fields.Binary(
        string="Tax amount by group",
        compute='_compute_local_invoice_taxes_by_group'
    )

    local_amount_residual = fields.Monetary(
        string='Amount Due',
        currency_field='company_currency_id',
        store=True,
        compute='_compute_amount'
    )

    @api.depends(
        'line_ids.price_subtotal',
        'line_ids.tax_base_amount',
        'line_ids.tax_line_id',
        'partner_id',
        'currency_id',
        'company_currency_id')
    def _compute_local_invoice_taxes_by_group(self):
        self._compute_invoice_taxes_by_group()
        for invoice in self:
            invoice._set_local_currency_values()
            local_amount_by_group = []
            if (invoice.is_sale_document() and invoice.currency_id
               and invoice.company_currency_id):
                lang_env = invoice.with_context(
                    lang=invoice.partner_id.lang).env
                invoice.show_other_currency = (bool)(
                    invoice.currency_id.id != invoice.company_currency_id.id)
                for group in invoice.amount_by_group:
                    amount = invoice.currency_id._convert(
                        group[1],
                        invoice.company_currency_id,
                        invoice.company_id, fields.Date.today()
                    )
                    base = invoice.currency_id._convert(
                        group[2],
                        invoice.company_currency_id,
                        invoice.company_id,
                        fields.Date.today()
                    )
                    lang_env_amount = formatLang(
                        lang_env, amount,
                        currency_obj=invoice.company_currency_id)
                    lang_env_base = formatLang(
                        lang_env, base,
                        currency_obj=invoice.company_currency_id)
                    local_amount_by_group.append((
                        group[0],
                        amount,
                        base,
                        lang_env_amount,
                        lang_env_base,
                        group[5],
                        group[6],
                    ))
            invoice.local_amount_by_group = local_amount_by_group

    def _set_local_currency_values(self):
        self.ensure_one()
        self.show_other_currency = False
        self.local_total_unsurdisc = 0.0
        self.local_amount_discount = 0.0
        self.local_amount_surchange = 0.0
        self.local_amount_untaxed = 0.0
        self.local_amount_total = 0.0
        self.local_amount_residual = 0.0
        self.local_amount_by_group = []

    def _calculate_company_currency_other_currency(self):
        _now = fields.Date.today()
        for invoice in self:
            invoice._set_local_currency_values()
            if (invoice.is_sale_document() and invoice.currency_id
               and invoice.company_currency_id):
                _date = invoice.invoice_date or _now
                invoice.show_other_currency = (bool)(
                    invoice.currency_id.id != invoice.company_currency_id.id)
                invoice.local_total_unsurdisc = invoice.currency_id._convert(
                    invoice.total_without_sur_disc,
                    invoice.company_currency_id,
                    invoice.company_id, _date
                )

                invoice.local_amount_discount = invoice.currency_id._convert(
                    invoice.amount_discount,
                    invoice.company_currency_id,
                    invoice.company_id, _date
                )

                invoice.local_amount_surchange = invoice.currency_id._convert(
                    invoice.amount_surchange,
                    invoice.company_currency_id,
                    invoice.company_id, _date
                )

                invoice.local_amount_untaxed = invoice.currency_id._convert(
                    invoice.amount_untaxed,
                    invoice.company_currency_id,
                    invoice.company_id, _date
                )

                invoice.local_amount_total = invoice.currency_id._convert(
                    invoice.amount_total,
                    invoice.company_currency_id,
                    invoice.company_id, _date
                )

                invoice.local_amount_residual = invoice.currency_id._convert(
                    invoice.amount_residual,
                    invoice.company_currency_id,
                    invoice.company_id, _date
                )

    @api.depends('currency_id', 'company_currency_id')
    def _compute_is_show_other_currency(self):
        self._calculate_company_currency_other_currency()

    @api.depends(
        'line_ids.debit',
        'line_ids.credit',
        'line_ids.amount_currency',
        'line_ids.amount_residual',
        'line_ids.amount_residual_currency',
        'line_ids.payment_id.state')
    def _compute_amount(self):
        super(AccountInvoice, self)._compute_amount()
        self._calculate_company_currency_other_currency()
