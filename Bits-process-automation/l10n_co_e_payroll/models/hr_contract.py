# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class HrContract(models.Model):
    _inherit = 'hr.contract'

    #check_telecommuting = fields.Boolean('Is teleworker', default=False)

    def copy(self, default=None):
        for record in self:
            if record.employee_id and record.employee_id.active == False:
                raise UserError(_('The employeee is archived.'))
            res = super(HrContract, self).copy(default)
            return res