# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class HrContract(models.Model):
    _inherit = 'hr.contract'

    contract_history_ids = fields.One2many(
        'hr.contract.history',
        'contract_id',
        string='History'
    )
    wage = fields.Monetary(
        'Wage', 
        required=True, 
        tracking=True, 
        help="Employee's monthly gross wage.",
        copy = False,
        default = 0,
    )

    @api.model
    def create(self, vals):
        res = super(HrContract, self).create(vals)
        self.addSalaryHistory(vals, res.id)
        return res

    def write(self, vals):
        self.addSalaryHistory(vals, self.id)
        return super(HrContract, self).write(vals)

    def addSalaryHistory(self, vals, id):
        if (
            vals.get('wage', False) and
            self.wage != 0 and
            vals['wage'] != self.wage
        ):
            self.env['hr.contract.history'].create({
                'contract_id': id,
                'date': datetime.now(),
                'description': _('Salary Change'),
                '_type': 'wage',
                'amount': vals['wage'],
                'last_salary': self.wage,
                'adjusment_date': datetime.now()
            })
