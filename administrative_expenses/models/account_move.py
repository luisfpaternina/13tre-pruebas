from odoo import models, fields, api, _
import logging

class AccountMove(models.Model):
    _inherit = 'account.move'

    is_validate = fields.Boolean(string="Validate")


    # @api.onchange('is_validate')
    def _validate_subscription(self):
        for record in self:
            sale_obj = record.env['sale.order'].search([('name', '=', record.invoice_origin)])
            if sale_obj:
                logging.info('######################################')
                record.is_validate = True
            else:
                record.is_validate = False


    @api.model
    def create(self, vals):
        rec = super(AccountMove, self).create(vals)
        self._validate_subscription()
        logging.info("***************************************************")       
        return rec
