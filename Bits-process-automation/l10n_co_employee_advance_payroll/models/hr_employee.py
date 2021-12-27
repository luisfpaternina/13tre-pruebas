from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from ast import literal_eval
import logging


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    high_risk_pension = fields.Boolean(
        'High pension risk',
        compute='_check_high_risk_pension',
        default=False
    )
    integral_salary = fields.Boolean(
        'Integral Salary',
        compute='_check_integral_salary',
        default=False
    )

    def get_config_rules(self, record, param):
        str_ids = self.env['ir.config_parameter'].sudo()\
            .get_param('many2many.' + param)
        if str_ids:
            _ids = literal_eval(str(str_ids))
            if record.contract_id and record.contract_id.structure_type_id \
                    and record.contract_id.structure_type_id.id in _ids:
                return True
        _ids = literal_eval(str_ids)
        if record.contract_id and record.contract_id.structure_type_id \
           and record.contract_id.structure_type_id.id in _ids:
            return True
        return False

    @api.onchange('name')
    def _check_high_risk_pension(self):
        for record in self:
            record.high_risk_pension = True \
                if record.contract_id and \
                record.contract_id.high_risk_pension\
                else False

    @api.onchange('name')
    def _check_integral_salary(self):
        for record in self:
            record.integral_salary = self.get_config_rules(
                record,
                'integral_structure_type_payroll_ids'
            )
