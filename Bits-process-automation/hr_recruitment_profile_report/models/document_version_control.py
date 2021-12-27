# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class DocumentVersionControl(models.Model):
    _inherit = 'document.version.control'

    job_id = fields.Many2one(
        string='Job',
        comodel_name='hr.job',
    )

    is_implement_model = fields.Boolean(string="Is Implement Model")

    def _get_currect_model(self,vals):
        result = False
        if vals.get('job_id', False):
            result = self.env['ir.model'].search([('model', '=', 'hr.job')])
        return result.id if result else False

    @api.model
    def create(self, vals):
        if self.is_implement_model or vals.get('is_implement_model', False):
            vals['model_id'] = self._get_currect_model(vals)
        result = super(DocumentVersionControl, self).create(vals)
        return result

    _sql_constraints = [
        ('uk_hr_recruitment_profile_report',
         'unique(job_id, version)',
         'You cannot have the same version for the same job.')
    ]
