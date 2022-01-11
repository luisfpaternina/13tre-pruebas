from odoo import models, fields, api, _
import logging

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _generate_lines(self):
        for record in self:
            record.order_line._validate_sale_subscription()

    


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    def _validate_sale_subscription(self):
        for record in self:
            subscription_obj = record.env['sale.subscription'].search([('display_name', '=', record.subscription_id.name)])
            if subscription_obj:
                subscription = self.env['sale.subscription'].create({
                    'recurring_invoice_line_ids': [(0, 0, {
                    'product_id': line.product_id.id,
                    'quantity': 1,
                    'price_unit': line.price_unit
                    }) for line in record.order_line]
                })
                return subscription
