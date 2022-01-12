from odoo import models, fields, api, _
import logging

class AccountMove(models.Model):
    _inherit = 'account.move'

    is_validate = fields.Boolean(
        string="Validate",
        compute="_validate_subscription")


    def _validate_subscription(self):
        for record in self:
            sale_obj = record.env['sale.order'].search([('name', '=', record.invoice_origin)])
            subscription_obj = record.env['sale.subscription'].search([])
            logging.info("MATHIASSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS")
            logging.info(subscription_obj)
            for s in subscription_obj:
                if sale_obj and record.invoice_date > record.invoice_date_due:
                    record.is_validate = True
                    if s in sale_obj.order_line.subscription_id:
                        s.display_name
                        logging.info("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
                        logging.info(s.display_name)
                        vals = {
                        'partner_id': s.partner_id.id,
                        'recurring_invoice_line_ids': [(0, 0, {
                            'product_id': s.recurring_invoice_line_ids.product_id.id,
                            'name': 'Gasto administrativo',
                            'price_unit': 2500,
                            'quantity': 1,
                            'uom_id': s.recurring_invoice_line_ids.uom_id.id,
                            })]
                        }
                        logging.info("mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm")
                        logging.info(vals)
                        s.write(vals)
                    #break
                else:
                    record.is_validate = False
