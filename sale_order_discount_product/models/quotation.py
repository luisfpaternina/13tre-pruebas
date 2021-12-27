# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Quotation(models.Model):
    _inherit = 'sale.order.line'

    total_sale_value_discount = fields.Monetary(
        string='Price unit with discount',
        readonly=True,
        compute='_calculate_sale_value_discount',
    )

    valid_in_category_id = fields.Boolean(
        invisible=True,
        default=True,
        compute="_calculate_valid_in_category"
    )

    valid_discount = fields.Boolean(
        related="order_id.valid_discount"
    )

    @api.depends('price_unit', 'product_uom_qty', 'discount')
    def _calculate_sale_value_discount(self):
        for record in self:
            total_discount = (record.price_unit*record.discount)/100
            record.total_sale_value_discount = round(
                (record.price_unit - total_discount), 0
            )

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(
                price, line.order_id.currency_id,
                line.product_uom_qty, product=line.product_id,
                partner=line.order_id.partner_shipping_id
            )
            line.update({
                'price_tax': sum(
                    t.get('amount', 0.0) for t in taxes.get('taxes', [])
                ),
                'price_total': taxes['total_included'],
                'price_subtotal': (
                    self.round_higher_multiple(taxes['total_excluded'])
                ),
            })
            if (
                self.env.context.get('import_file', False)
                and not self.env.user.user_has_groups(
                    'account.group_account_manager'
                )
            ):
                line.tax_id.invalidate_cache(
                    ['invoice_repartition_line_ids'], [line.tax_id.id]
                )

    def round_higher_multiple(self, subtotal):
        if len(str(int(subtotal))) >= 2:
            last_dig = int(str(int(subtotal))[-1])
            alast_dig = int(str(int(subtotal))[-2])
            if alast_dig < 5 and last_dig + alast_dig > 0:
                subtotal += 100
        elif subtotal > 0:
            last_dig = int(str(int(subtotal))[-1])
            subtotal += 100
        return round(subtotal, -2)

    @api.depends('product_id')
    def _calculate_valid_in_category(self):
        for record in self:
            if record.product_id.categ_id.apply_discount_table:
                record.valid_in_category_id = True
            else:
                record.valid_in_category_id = False


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    discount_order = fields.Float(
        string="Discount (%)",
        help=(
            'This field assigns the discount '
            'in each of the budget lines'
        )
    )

    approver_discount_id = fields.Many2one(
        'res.users',
        'Sale Order Discount Approver',
        readonly=True,
        copy=False,
        track_visibility='onchange'
    )

    @api.constrains(
        'discount_order',
        'order_line.discount',
        'order_line.product_uom_qty',
        'order_line.price_unit'
    )
    def _calculate_sale_discount(self):
        for record in self:
            sale_ol_obj = self.env['sale.order.line'].search(
                [('order_id', '=', record.id)]
            )
            for line in sale_ol_obj:
                if (
                    line.product_id.categ_id.apply_discount_table and
                    record.discount_order != 0
                ):
                    line.write({'discount': record.discount_order})
                    record.validation_for_discount()
