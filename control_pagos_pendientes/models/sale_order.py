# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date




class SaleOrder(models.Model):
    _inherit = ['sale.order']

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()

        # Para activar el modal, el cliente debe de tener impagos
        cliente = self.partner_id
        invoice_with_debt = ""
        today = date.today()
        AM = self.env['account.move']
        AML = self.env['account.move.line']

        facturas = AM.search([('partner_id', '=', cliente.id)])

        if facturas:
            for factura in facturas:
                factura_id = factura.id
                lineas = AML.search([('move_id.id','=', factura_id)])

                if lineas:
                    for linea in lineas:
                        if linea.account_internal_type == "receivable":
                            if linea.date_maturity != False:
                                if linea.date_maturity != "" and linea.date_maturity < today:
                                    if linea.amount_residual > 0:
                                        invoice_with_debt = invoice_with_debt + " - " + factura.name
            if invoice_with_debt != "":
                view = self.env.ref('control_pagos_pendientes.alert_debt_wizard_form')
                return {'name': _('Aviso importante Interno'),
                        'view_type': 'form',
                        'view_mode': 'form',
                        'target': 'new',
                        'res_model': 'alert.debt.wizard',
                        'view_id': view.id,
                        'views': [(view.id, 'form')],
                        'type': 'ir.actions.act_window',
                        'context': {'invoices_with_debt': invoice_with_debt}
                        }
#         else:
#             view = self.env.ref('control_pagos_pendientes.alert_debt_wizard_form')
#             return {'name': _('Aviso importante 1'),
#                     'view_type': 'form',
#                     'view_mode': 'form',
#                     'target': 'new',
#                     'res_model': 'alert.debt.wizard',
#                     'view_id': view.id,
#                     'views': [(view.id, 'form')],
#                     'type': 'ir.actions.act_window',
#                     'context': {}
#                     }
