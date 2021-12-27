# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    valid_discount = fields.Boolean(
        invisible=True,
        default=True,
    )

    send_approval_discount = fields.Boolean()
    send_approval_freight = fields.Boolean()

    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        context = self.env.context
        if 'rejected_by_a_superior' in context:
            if 'reject_discount' in context:
                self.approver_discount_id = False
                self.valid_discount = False
            elif 'reject_freight' in context:
                self.approver_freight_id = False
                self.recompute_delivery_price = True
        else:
            if self.approver_discount_id:
                self.valid_discount = False
            if self.approver_freight_id:
                self.recompute_delivery_price = True
            self.approver_discount_id = False
            self.approver_freight_id = False
        self.send_approval_discount = False
        self.send_approval_freight = False
        return res

    @api.onchange('order_line', 'discount_order')
    def validation_for_discount(self):
        for record in self:
            discount_table = record.env['discount.table'].search([])
            list_lines = []
            for line in record.order_line:
                if (
                    line.product_id.categ_id.apply_discount_table and
                    line.discount > 0
                ):
                    for discount in discount_table:
                        if (
                            line.product_uom_qty >= discount.min_quantity and
                            line.product_uom_qty <= discount.max_quantity
                        ):
                            if (
                                line.discount >= discount.min_discount and
                                line.discount <= discount.max_discount
                            ):
                                mb = self.env.company.min_gross_margin
                                total_cost = (
                                    line.product_id.standard_price *
                                    (1 + (mb / 100))
                                )
                                total_price_unit = (
                                    line.total_sale_value_discount
                                )
                                if total_price_unit > total_cost:
                                    list_lines.append(line)
                elif line.discount == 0:
                    list_lines.append(line)
                else:
                    list_lines.append(line)
                    line.valid_in_category_id = False

                if len(list_lines) >= len(record.order_line):
                    record.valid_discount = True
                else:
                    record.valid_discount = False

    @api.onchange('order_line')
    def validate_discount_line_without_order_discount(self):
        for record in self:
            record.write({'discount_order': 0})

    def action_confirm_flow(self):
        context = self.env.context
        if 'approve_by_a_superior' in context:
            message = (
                '<i>After the quote has been sent for approval, '
                'it has been <strong>approved.</strong></i>'
            )
            if 'approve_freight' in context:
                self.message_post(
                    body=_(
                        '<strong>Freight: </strong>' +
                        message
                    )
                )
                self.approver_freight_id = self.env.user.id
                self.recompute_delivery_price = False
            if 'approve_discount' in context:
                self.message_post(
                    body=_(
                        '<strong>Discount: </strong>' +
                        message
                    )
                )
                self.approver_discount_id = self.env.user.id
                self.valid_discount = True
            approve = False
            if self.send_approval_discount and self.send_approval_freight:
                if self.approver_discount_id and self.approver_freight_id:
                    approve = True
            elif self.send_approval_discount:
                if self.approver_discount_id:
                    approve = True
            elif self.send_approval_freight:
                if self.approver_freight_id:
                    approve = True

            if approve:
                self.update({
                    'state': 'approve_superior'
                })

    def send_for_approval(self):
        for record in self:
            if not record.valid_discount:
                record.send_approval_discount = True
            if record.recompute_delivery_price:
                record.send_approval_freight = True
            record.update(
                {
                    'state': 'waiting_for_approval'
                }
            )
