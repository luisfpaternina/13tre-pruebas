from odoo import models, fields, api, _
from ast import literal_eval


class HrPayrollApprovalSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    emails_job_ids = fields.Many2many(
        'hr.job',
        'emails_job_ids_table',
        string='Emails jobs'
    )

    def set_values(self):
        res = super(HrPayrollApprovalSetting, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.emails_job_ids', self.emails_job_ids.ids)
        return res

    @api.model
    def get_values(self):
        res = super(HrPayrollApprovalSetting, self).get_values()
        with_user = self.env['ir.config_parameter'].sudo()
        emails_job_ids = with_user.get_param(
            'many2many.emails_job_ids')
        res.update(
            emails_job_ids=[(6, 0, literal_eval(emails_job_ids))]
            if emails_job_ids else False)
        return res
