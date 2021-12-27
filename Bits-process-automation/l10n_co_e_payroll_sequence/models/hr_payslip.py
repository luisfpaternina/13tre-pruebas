# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HrPayslipInherit(models.Model):
    _inherit = 'hr.payslip'

    def action_payslip_done(self):
        result = super(HrPayslipInherit, self).action_payslip_done()
        if self.struct_id.sequence_id:
            id_sequence = self.struct_id.sequence_id.id
            self.number = self.struct_id.sequence_id.next_by_id(id_sequence)
        return result
