# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from ast import literal_eval


class HrEmployeeSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    percentage_workload = fields.Float(
        string="Percentage workload",
        default=100,
        readonly=False
    )

    @api.model
    def get_values(self):
        res = super(HrEmployeeSetting, self).get_values()
        with_user = self.env['ir.config_parameter'].sudo()
        percentage_workload = with_user.get_param('percentage_workload')
        res.update(
            percentage_workload=float(percentage_workload)
        )
        return res

    def set_values(self):
        super(HrEmployeeSetting, self).set_values()
        param = self.env['ir.config_parameter']
        param.set_param(
            'percentage_workload',
            float(self.percentage_workload)
            if self.percentage_workload else 100
        )
