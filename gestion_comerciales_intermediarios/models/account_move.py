# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class AccountMove(models.Model):
    _inherit = ['account.move']

    total_liquidacion = fields.Float(string="Total liquidacion", required=False, compute="_calcular_liquidacion")
    fecha_liquidado = fields.Datetime(string="")
    es_liquidado = fields.Boolean(string="Liquidado")
    intermediario_partner_id = fields.Many2one('res.users', related='partner_id.intermediario_id',
                                               string='Intermediario', readonly=True,  store=True) #Alberto.26/07/21. Se pone a True para poder agrupar por ese campo.

    def _calcular_liquidacion(self):
        for record in self:
            total_liquidacion = 0
            intermediario = record.partner_id.intermediario_id

            if intermediario:
                base_imponible = record.amount_untaxed
                porcentaje_comision = record.partner_id.porcentaje_intermediario
                total_liquidacion = (base_imponible * porcentaje_comision) / 100

            record.total_liquidacion = total_liquidacion

    def marcar_liquidaciones_como_realizadas(self):
        facturas = self.ids

        for factura in facturas:
            AM = self.env['account.move']
            detalle_factura = AM.search([('id','=', factura)])
            detalle_factura.write({'es_liquidado': True})


    #Alberto.23/07/21. Se debe calcular con las líneas de las facturas porque hay que tener en cuenta el tipo de producto. Creo nuevo campo para no eliminar el original.
    liquidation_amount = fields.Float(string="Total liquidacion", required=False, compute="_compute_liquidation_amount")

    @api.depends('intermediario_partner_id', 'partner_id.porcentaje_intermediario', 'amount_untaxed')
    def _compute_liquidation_amount(self):
        for record in self:
            total_liquidacion = 0
            intermediario = record.intermediario_partner_id
            if record.type == 'out_invoice' and intermediario:
                base_imponible = sum(record.invoice_line_ids.search([('company_id', '=', record.company_id.id), ('move_id', '=', record.id), ('product_type', '=', 'product')]).mapped('price_subtotal'))
                porcentaje_comision = record.partner_id.porcentaje_intermediario
                total_liquidacion = (base_imponible * porcentaje_comision) / 100
            record.liquidation_amount = total_liquidacion