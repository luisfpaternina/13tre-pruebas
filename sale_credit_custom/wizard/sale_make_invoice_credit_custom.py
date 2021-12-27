# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleConfirmCreditPayment(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    payment_credit = fields.Boolean()
    credit = fields.Many2one(
        'credit',
        string="Credit to use",
        domain="[('res_partner_id', '=', partner_id)]"
    )
    partner_id = fields.Many2one(
        'res.partner',
        compute="_get_partner_id_field"
    )

    @api.onchange('advance_payment_method')
    def _get_partner_id_field(self):
        sale_orders = self.env['sale.order'].browse(
            self._context.get('active_ids', [])
        )
        if len(sale_orders) == 1:
            self.partner_id = sale_orders[0].partner_id

    def create_invoices(self):
        sale_orders = self.env['sale.order'].browse(
            self._context.get('active_ids', [])
        )

        if self.advance_payment_method == 'delivered':
            moves_returned = sale_orders._create_invoices(
                final=self.deduct_down_payments
            )
            if self.payment_credit:
                for move in moves_returned:
                    move.update({
                        'credit_payment': self.payment_credit,
                        'credit': self.credit
                    })
        else:
            # Create deposit product if necessary
            if not self.product_id:
                vals = self._prepare_deposit_product()
                self.product_id = self.env['product.product'].create(vals)
                self.env['ir.config_parameter'].sudo().set_param(
                    'sale.default_deposit_product_id', self.product_id.id
                )

            sale_line_obj = self.env['sale.order.line']
            for order in sale_orders:
                amount, name = self._get_advance_details(order)

                if self.product_id.invoice_policy != 'order':
                    raise UserError(
                        _(
                            'The product used to invoice a down payment '
                            'should have an invoice policy set to "Ordered '
                            'quantities". Please update your deposit product '
                            'to be able to create a deposit invoice.'
                        )
                    )
                if self.product_id.type != 'service':
                    raise UserError(
                        _(
                            "The product used to invoice a down payment "
                            "should be of type 'Service'. Please "
                            "use another product or update this product."
                        )
                    )
                taxes = self.product_id.taxes_id.filtered(
                    lambda r: not order.company_id or
                    r.company_id == order.company_id
                )
                if order.fiscal_position_id and taxes:
                    tax_ids = order.fiscal_position_id.map_tax(
                        taxes, self.product_id, order.partner_shipping_id
                    ).ids
                else:
                    tax_ids = taxes.ids
                analytic_tag_ids = []
                for line in order.order_line:
                    analytic_tag_ids = [
                        (4, analytic_tag.id, None)
                        for analytic_tag
                        in line.analytic_tag_ids
                    ]

                so_line_values = self._prepare_so_line(
                    order, analytic_tag_ids, tax_ids, amount
                )
                so_line = sale_line_obj.create(so_line_values)
                invoice = self._create_invoice(order, so_line, amount)
                if self.payment_credit:
                    invoice.update({
                        'credit_payment': self.payment_credit,
                        'credit': self.credit
                    })
        if self._context.get('open_invoices', False):
            return sale_orders.action_view_invoice()
        return {'type': 'ir.actions.act_window_close'}
