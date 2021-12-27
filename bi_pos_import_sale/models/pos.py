
from datetime import datetime, timedelta, date
import dateutil.parser
from itertools import groupby
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import (
    float_is_zero,
    float_compare,
    DEFAULT_SERVER_DATETIME_FORMAT
)
from odoo.tools.misc import formatLang
from odoo.tools import html2plaintext
import odoo.addons.decimal_precision as dp


class PosConfiguration(models.Model):
    _inherit = 'pos.config'

    # The configuration parameters for the list
    # of sales orders (sale.order), are invisible,
    # remove the visibility attribute to be able
    # to see these parameters

    check = fields.Boolean(
        string='Import Sale Order',
        default=False,
        invisible=True
    )
    load_orders_days = fields.Integer(
        'Load Orders of Last Days',
        invisible=True
    )
    load_draft_sent = fields.Boolean(
        string='Load only draft/sent sale orders',
        default=False,
        invisible=True
    )
    cancle_order = fields.Boolean(
        string='Cancel Sale Order after Import',
        default=False,
        invisible=True
    )


class InheritPOSOrder(models.Model):
    _inherit = 'pos.order'
    sale_order_ids = fields.Many2many(
        'sale.order',
        string="Imported Sale Order(s)"
    )

    def search_all_sale_order(self, config_id, l_date):
        final_order = []
        so_ids = []
        sale_order = []
        last_day = datetime.strptime(
            l_date,
            DEFAULT_SERVER_DATETIME_FORMAT
        )
        config = self.env['pos.config'].browse(config_id)
        if config.load_orders_days > 0:
            if config.load_draft_sent:
                sale_orders = self.env['sale.order'].search([
                    ('date_order', '>=', last_day),
                    '|',
                    ('state', '=', 'draft'),
                    ('state', '=', 'sent'),
                ])
            else:
                sale_orders = self.env['sale.order'].search([
                    ('date_order', '>=', last_day)
                ])
        else:
            if config.load_draft_sent:
                sale_orders = self.env['sale.order'].search([
                    '|',
                    ('state', '=', 'draft'),
                    ('state', '=', 'sent')
                ])

            else:
                sale_orders = self.env['sale.order'].search([])

        for s in sale_orders:
            vals1 = {
                'id': s.id,
                'name': s.name,
                'state': s.state,
                'partner_id': [s.partner_id.id, s.partner_id.name],
                'user_id': [s.user_id.id, s.user_id.name],
                'amount_untaxed': s.amount_untaxed,
                'order_line': s.order_line.ids,
                'amount_tax': s.amount_tax,
                'amount_total': s.amount_total,
                'company_id': [s.company_id.id, s.company_id.name],
                'date_order': s.date_order
            }
            final_order.append(vals1)

        return final_order

    def _order_fields(self, ui_order):
        res = super(InheritPOSOrder, self)._order_fields(ui_order)
        config = self.env['pos.session'].browse(
            ui_order['pos_session_id']
        ).config_id
        if config.cancle_order:
            if 'imported_sales' in ui_order and ui_order.get('imported_sales'):
                so = ui_order['imported_sales'].split(',')
                so.pop()
                so_ids = []
                sale_orders = []
                for odr in so:
                    sale = self.env['sale.order'].browse(int(odr))
                    if sale:
                        so_ids.append(sale.id)
                        sale_orders.append(sale)
                res.update({
                    'sale_order_ids': [(6, 0, so_ids)]
                })
                for s in sale_orders:
                    s.action_cancel()
        return res

    def return_new_order_line(self):
        orderlines = self.env['sale.order.line'].search([(
            'order_id.id', '=', self.id)
        ])
        final_lines = []
        for line in orderlines:
            vals1 = {
                    'discount': line.discount,
                    'id': line.id,
                    'order_id': [line.order_id.id, line.order_id.name],
                    'price_unit': line.price_unit,
                    'product_id': [line.product_id.id, line.product_id.name],
                    'product_uom_qty': line.product_uom_qty,
                    'price_subtotal': line.price_subtotal,
                }
            final_lines.append(vals1)
        return final_lines

    def sale_order_line(self):
        orderlines = self.env['sale.order.line'].search([])
        final_lines = []
        for line in orderlines:
            vals1 = {
                    'discount': line.discount,
                    'id': line.id,
                    'order_id': [line.order_id.id, line.order_id.name],
                    'price_unit': line.price_unit,
                    'product_id': [line.product_id.id, line.product_id.name],
                    'product_uom_qty': line.product_uom_qty,
                    'price_subtotal': line.price_subtotal,
            }
            final_lines.append(vals1)
        return final_lines
