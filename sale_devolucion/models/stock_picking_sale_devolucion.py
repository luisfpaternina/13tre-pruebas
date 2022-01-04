# Copyright 2020 Raul Carbonell
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _

import logging
_logger=logging.getLogger(__name__)

class ReturnPickingSaleDevolucion(models.Model):
    _inherit = "stock.picking"

    #Al modificar un stock.piking, si es de tipo retorno y tiene Pedido
    #y este pedido tiene status_devolucio='pendiente'
    #se modificará a 'completada'
    def write(self, vals):
        _logger.info("Actualiza")
        res = super(ReturnPickingSaleDevolucion, self).write(vals)

        picking_type = self.picking_type_id
        sale_id=self.sale_id

        if sale_id and picking_type.id==1:
            pedido=self.env["sale.order"].browse(sale_id.id)
            if pedido.status_devolucion=="pendiente":
                pedido.status_devolucion="completada"

        return res
