
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class SendEmailPayrollApprovalInherit(models.TransientModel):
    _inherit = 'send.email.payroll.approval'

    def send_and_print_action(self):
        for payslip in self.payslip_ids:
            payslip.check_send_approval = True
        res = super(SendEmailPayrollApprovalInherit, self).send_and_print_action()
        return res