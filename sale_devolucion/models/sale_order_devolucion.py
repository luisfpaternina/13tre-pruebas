# Copyright 2020 Raul Carbonell
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _

class SaleOrderDevolucion(models.Model):
    _inherit = "sale.order"

    status_devolucion = fields.Selection(
        string="Estado Devolución",
        selection=[
                ('solicitud', 'Solicitud de Devolución'),
                ('pendiente', 'Pendiente de Devolución'),
                ('completada', 'Devolución Completada'),
                ('rechazada', 'Rechazada Devolución'),
        ],
        tracking=True,
    )

    motivo_devolucion = fields.Text(required=False, default=False)

    cantidad_devolver = fields.Text(required=False, default=False)


    #Si cantidad entregada > 0, hay alqo que se puede devolver.
    cantidad_entregada_qty = fields.Integer(
        string="Cantidad Entregada",
        compute='_compute_cantidad_entregada_qty',
    )

    def _compute_cantidad_entregada_qty(self):
        for order in self:
            cantidad=0
            orderlines=order.order_line
            for orderline in orderlines:
                cantidad=cantidad+orderline.qty_delivered

            order.cantidad_entregada_qty=cantidad
            
