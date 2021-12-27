# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging
from odoo.exceptions import AccessError, \
    UserError, RedirectWarning, ValidationError, Warning
_logger = logging.getLogger(__name__)


class AccountCollectivePayments(models.TransientModel):
    _inherit = 'account.collective.payments.wizard'
    check_f = fields.Boolean(default=False)
    payment_date = fields.Date('Fecha de pago')
    payment_method_dian_id = fields.Many2one(
        'payment.method',
        string='Metodo de pago',
        required=True,
        )
    payment_way_dian_id = fields.Many2one(
        'payment.way',
        string='Metodo de pago',
        required=True,
        )
    supplier_payment = fields.Boolean('Pago proveedor')

    def generate_payments_action(self):
        res = super(AccountCollectivePayments, self).generate_payments_action()
        self.generate_payments_action_t()
        return res
    """The methods in this file are going to be apply only
    to do payroll's payment"""
    def generate_payments_check_f(self):
        answer = True if len(self.line_ids) > 0 else False
        return answer

    def check_journal_name(self):
        ans = True if self.journal_id_f.name == 'Nomina' else False
        return ans

    def check_payments_and_journal(self):
        answer = self.generate_payments_check_f()
        ans = self.check_journal_name()
        result = True if answer is True and ans is True else False
        return result

    def generate_payments_action_t(self):
        set_line = set()
        self.check_f = self.check_payments_and_journal()
        if self.check_f is True:
            for line in self.line_ids:
                set_line.add(line.move_id.id)
            list_hr = [self.env['hr.payslip'].search([(
                'move_id', '=', elemen
                )]) for elemen in set_line]
            for hr in list_hr:
                hr.payment_method_id = self.payment_method_dian_id.id
                hr.payment_way_id = self.payment_way_dian_id.id
                hr.payment_date = self.payment_date
            return
        return
