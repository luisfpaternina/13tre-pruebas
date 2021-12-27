from typing import Sequence
from odoo import models, fields, api, _
from datetime import datetime


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'
    _description = 'Extended Hr Applicant'

    internal_request = fields.Many2one(
        'hr.employee.internal.request',
        # required=True,
        string=_('Internal Request Link')
    )
    identification_number = fields.Char(
        index=True, string=_('Identification Number')
    )
    status = fields.Selection(
        [('pre', 'Pre Seleccionados'),
         ('desc', 'Descartados')],
        string=_('Status'))

    eval_comment = fields.Text(
        string=_('Evaluator Comment'), tracking=True)

    def get_internal_request(self, job_id):
        internal_request_ids = self\
            .env['hr.employee.internal.request']\
            .search([
                ('job_position', '=', job_id),
                ('stage_id.sequence', '=', 4)
            ])
        return internal_request_ids

    @api.model
    def create(self, vals):
        info_internal = self.get_internal_request(vals.get('job_id', False))
        if info_internal:
            vals['internal_request'] = info_internal[0].id
        info_applicant = super(HrApplicant, self).create(vals)
        return info_applicant

    def write(self, vals):
        for item in self:
            job_id = (
                vals.get('job_id')
                if vals.get('job_id', False)
                else item.job_id.id
            )
            info_internal = item.get_internal_request(job_id)

            vals['internal_request'] = (
                info_internal[0].id
                if info_internal
                else False
            )
        info_applicant = super(HrApplicant, self).write(vals)
        return info_applicant

    # This code make conflict because has ciclic reactive change
    # @api.onchange('internal_request')
    # def _onchange_internal_request(self):
    #     if not (self.job_id == False):
    #         info_job = self.internal_request.job_position
    #         # print(f'Job id {info_job}')
    #         self.job_id = (info_job.id if info_job else False)
    #         print(f'Job id {self.job_id}')

    @api.onchange('job_id')
    def _onchange_job_id(self):
        # print(f'onchange self {self.internal_request}')
        if not self.internal_request:
            info_internal = self.get_internal_request(self.job_id.id)
            # print(f'info_internal {info_internal} job_id {self.job_id.id}')
            self.internal_request = (
                info_internal[0].id if info_internal else False)
            # print(f'self.internal_request {self.internal_request}')
