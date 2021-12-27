# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountCollectivePayments(models.TransientModel):
    _inherit = 'account.collective.payments.wizard'

    payment_method_dian_id = fields.Many2one(
                                            'payment.method',
                                            String='Payment Method'
                                            )
    payment_way_dian_id = fields.Many2one(
                                        'payment.way',
                                        string="Payment Way"
                                        )
    payment_date = fields.Date('Payment date')
