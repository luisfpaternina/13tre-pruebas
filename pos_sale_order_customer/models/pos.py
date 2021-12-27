# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
import logging
import psycopg2
import pytz
from functools import partial

_logger = logging.getLogger(__name__)


class POS(models.Model):
    _inherit = "pos.order"

    value = fields.Char(default='2')

    origin_invoice_pos_id = fields.Char(
        string='Invoice Origin',
        readonly=True,
        invisible=True,
    )

    origin_sale_order_pos_id = fields.Char(
        string='Sale Order Origin',
        readonly=True,
        invisible=True,
    )

    def create_picking(self):
        res = False
        moves = self.env['account.move']
        account_move_obj = self.env['account.move'].search([
            ('id', '=', self.origin_invoice_pos_id)
        ])
        so_obj = self.env['sale.order'].search([
            ('id', '=', self.origin_sale_order_pos_id)
        ])
        if self.origin_invoice_pos_id and account_move_obj.invoice_origin:
            if account_move_obj.state == 'draft':
                account_move_obj.action_post()
            sale_order_obj = self.env['sale.order'].search([
                ('name', '=', account_move_obj.invoice_origin)
            ])
            self.picking_id = sale_order_obj.picking_ids[0]
            account_move_obj.invoice_payment_state = 'paid'
            res = True
            for order in self:
                order.write({
                    'account_move': account_move_obj[0].id,
                    'state': 'invoiced'
                })
                moves += account_move_obj

        elif self.origin_sale_order_pos_id and so_obj.state == 'sale':
            self.picking_id = so_obj.picking_ids[0]
            res = True
        else:
            if self.origin_invoice_pos_id:
                if account_move_obj.state == 'draft':
                    account_move_obj.action_post()
                account_move_obj.invoice_payment_state = 'paid'
                for order in self:
                    order.write({
                        'account_move': account_move_obj[0].id,
                        'state': 'invoiced'
                    })
                    moves += account_move_obj

            res = super(POS, self).create_picking()
        return res

    @api.model
    def _process_order(self, order, draft, existing_order):
        """Create or update an pos.order from a given dictionary.

        :param pos_order: dictionary representing the order.
        :type pos_order: dict.
        :param draft: Indicate that the pos_order is not validated yet.
        :type draft: bool.
        :param existing_order: order to be updated or False.
        :type existing_order: pos.order.
        :returns number pos_order id
        """
        order = order['data']
        pos_session = self.env['pos.session'].browse(order['pos_session_id'])
        if pos_session.state == 'closing_control'\
                or pos_session.state == 'closed':
            order['pos_session_id'] = self._get_valid_session(order).id

        pos_order = False
        if not existing_order:
            pos_order = self.create(self._order_fields(order))
        else:
            pos_order = existing_order
            pos_order.lines.unlink()
            order['user_id'] = pos_order.user_id.id
            pos_order.write(self._order_fields(order))

        self._process_payment_lines(order, pos_order, pos_session, draft)

        if not draft:
            try:
                pos_order.action_pos_order_paid()
            except psycopg2.DatabaseError:
                # do not hide transactional errors,
                # the order(s) won't be saved!
                raise
            except Exception as e:
                _logger.error(
                    'Could not fully process the POS Order: %s',
                    tools.ustr(e)
                )

        if pos_order.to_invoice and pos_order.state == 'paid':
            pos_order.action_pos_order_invoice()

            # Amarrar la factura a la Orden de Venta
            # account_move_obj = self.env['account.move'].search([
            #     ('id', '=', pos_order.origin_invoice_pos_id)
            # ])
            # so_obj = self.env['sale.order'].search([
            #     ('id', '=', pos_order.origin_sale_order_pos_id)
            # ])
            # if pos_order.origin_invoice_pos_id \
            #         and account_move_obj.invoice_origin:
            #     print("invoice")
            #     sale_order_obj = self.env['sale.order'].search([
            #         ('name', '=', account_move_obj.invoice_origin)
            #     ])
            #     # sale_order_obj.write({
            #     #     'invoice_origin_pos': pos_order.account_move,
            #     #     'is_pos_order_link': True
            #     # })
            # # elif pos_order.origin_sale_order_pos_id:
            # #     so_obj.write({
            # #         'invoice_origin_pos': pos_order.account_move,
            # #         'is_pos_order_link': True
            # #     })

        return pos_order.id

    @api.model
    def _order_fields(self, ui_order):
        process_line = partial(
            self.env['pos.order.line']._order_line_fields,
            session_id=ui_order['pos_session_id']
        )
        return {
            'user_id': ui_order['user_id'] or False,
            'session_id': ui_order['pos_session_id'],
            'lines': [
                process_line(line) for line in ui_order['lines']
            ] if ui_order['lines'] else False,
            'pos_reference': ui_order['name'],
            'sequence_number': ui_order['sequence_number'],
            'partner_id': ui_order['partner_id'] or False,
            'date_order': ui_order['creation_date'].replace('T', ' ')[:19],
            'fiscal_position_id': ui_order['fiscal_position_id'],
            'pricelist_id': ui_order['pricelist_id'],
            'amount_paid': ui_order['amount_paid'],
            'amount_total': ui_order['amount_total'],
            'amount_tax':  ui_order['amount_tax'],
            'amount_return':  ui_order['amount_return'],
            'company_id': self.env['pos.session'].browse(ui_order[
                'pos_session_id']).company_id.id,
            'to_invoice': (
                ui_order['to_invoice']
                if "to_invoice" in ui_order else False
            ),
            'origin_invoice_pos_id': ui_order['invoice_origin_pos'],
            'origin_sale_order_pos_id': ui_order['sale_order_origin_pos'],
        }

    def action_pos_order_invoice(self):
        moves = self.env['account.move']

        for order in self:
            # Force company for all SUPERUSER_ID action

            if order.account_move:
                moves += order.account_move
                continue

            if not order.partner_id:
                raise UserError(_('Please provide a partner for the sale.'))

            if order.origin_invoice_pos_id:
                account_origin = moves.search([
                    ('id', '=', order.origin_invoice_pos_id)
                ])
                order.write({
                    'account_move': account_origin[0].id,
                    'state': 'invoiced'
                })
                moves += account_origin

            else:
                move_vals = order._prepare_invoice_vals()
                new_move = order._create_invoice(move_vals)
                order.write({
                    'account_move': new_move.id,
                    'state': 'invoiced'
                })
                new_move.sudo().with_context(
                    force_company=order.company_id.id
                ).post()
                moves += new_move

        if not moves:
            return {}
        return {
            'name': _('Customer Invoice'),
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_move_form').id,
            'res_model': 'account.move',
            'context': "{'type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': moves and moves.ids[0] or False,
        }
