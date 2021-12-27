from odoo import api, fields, models, _
from odoo.tools import float_round


class HrPayslipEmployee(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    @api.onchange('structure_id')
    def _onchange_structure(self):
        list_employee = self.env['hr.employee']
        domain = [('state', '=', 'open')]
        if self.structure_id and self.structure_id.id:
            domain.append(('structure_type_id', '=',
                           self.structure_id.type_id.id))
        list_contract = self.env['hr.contract'].search(domain)
        for contract in list_contract:
            list_employee += contract.employee_id
        self.employee_ids = list_employee
