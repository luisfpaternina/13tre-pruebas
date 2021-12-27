# coding: utf-8

from odoo import api, fields, models, tools, _


class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'

    def _get_data_taxes_e_invoice_line(self, name=None):
        self.ensure_one()
        taxes_amount_dict = {}
        price_unit = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = self.tax_ids.compute_all(
            price_unit, quantity=self.quantity, currency=self.currency_id,
            product=self.product_id, partner=self.partner_id
        )
        for tax in taxes['taxes']:
            tax_rec = self.env['account.tax'].browse(tax['id'])
            tax['rate'] = tax_rec.amount
            tax['description'] = tax_rec.description
            tax['group'] = tax_rec.tax_group_id.name
            if tax_rec.tax_group_id.name == name:
                return tax
        return []

    def _get_computed_taxes(self):
        self.ensure_one()
        tax_ids = super(AccountInvoiceLine, self)._get_computed_taxes()
        if self.move_id.is_sale_document():
            category_to_apply = self.move_id.get_category_to_apply()
            tax_ids = tax_ids.filtered(
                lambda tax: (
                    (
                        tax.type_of_tax in category_to_apply
                        and tax.type_of_tax.retention
                    ) or not tax.type_of_tax.retention
                )
            )
            tax_ids |= self.move_id.company_id.account_sale_tax_ids
        return tax_ids

    def _get_taxes_by_type(self, retention=None):
        self.ensure_one()
        taxes_amount_dict = {}
        price_unit = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = self.tax_ids.compute_all(
            price_unit, quantity=self.quantity, currency=self.currency_id,
            product=self.product_id, partner=self.partner_id
        )
        result = []
        for tax in taxes['taxes']:
            tax_rec = self.env['account.tax'].browse(tax['id'])
            if (retention is not None and
               tax_rec.type_of_tax.retention != retention) or \
               tax_rec.tax_group_fe == 'nap_fe':
                continue

            tax['rate'] = tax_rec.amount
            tax['description'] = tax_rec.description
            tax['group'] = tax_rec.tax_group_id.name
            tax['code'] = tax_rec.type_of_tax.code
            tax['name'] = tax_rec.type_of_tax.name
            tax['retention'] = tax_rec.type_of_tax.retention
            result.append(tax.copy())
        return result

    def _get_surchange_discount_by_line(self):
        return super(AccountInvoiceLine, self).\
            _get_surchange_discount_by_line()

    @api.depends(
        'amount_residual',
        'date',
        'amount_residual_currency',
        'currency_id',)
    def _compute_amount_to_show(self):
        for line in self:
            currency = line.company_id.currency_id
            amount_to_show = currency._convert(
                abs(line.amount_residual),
                line.move_id.currency_id,
                line.move_id.company_id,
                line.date or fields.Date.today()
            )
            line.amount_to_show = abs(line.amount_residual_currency) \
                if line.currency_id and \
                line.currency_id == line.move_id.currency_id\
                else amount_to_show

    amount_to_show = fields.Monetary(
        string='Amount',
        currency_field='company_currency_id',
        compute='_compute_amount_to_show')

    # def _get_computed_name(self):
    #     self.ensure_one()
    #     res = super(AccountInvoiceLine, self)._get_computed_name()
    #     if self.journal_id.type == 'sale' and self.move_id.ref:
    #         res = self.move_id.ref
    #     return res
