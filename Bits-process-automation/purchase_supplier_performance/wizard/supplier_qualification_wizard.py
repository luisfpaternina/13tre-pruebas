from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SupplierQualificationWizard(models.TransientModel):
    _name = 'supplier.qualification.wizard'

    performance = fields.Selection(string='Performance', selection=[
        ('0', 'Very Bad'), ('1', 'Bad'), ('2', 'Regular'), ('3', 'Good')],
        default='0'
    )
    description = fields.Char(string='Description')

    def create_partner_performance(self):
        partner_performance = self.env['res.partner.performance']
        order_id = self.env['purchase.order'].browse([
            self.env.context.get('order_id')])
        partner_performance.create({
            'partner_id': self.env.context.get('partner_id'),
            'performance': self.performance,
            'description': self.description,
            'order_id': order_id.id,
            'type': self.env.context.get('type_qualification')
        })
        order_id.write({
            'has_qualification': True
        })
