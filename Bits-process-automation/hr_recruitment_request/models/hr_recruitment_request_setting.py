from odoo import models, fields, api, _
from ast import literal_eval

class HrRecruitmentRequestSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    profile_email_ids = fields.Many2many(
        'hr.job',
        'profile_email_ids_table',
        string='Profile Emails'
    )

    def set_values(self):
        res = super(HrRecruitmentRequestSetting, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.profile_email_ids', self.profile_email_ids.ids)
        return res

    @api.model
    def get_values(self):
        res = super(HrRecruitmentRequestSetting, self).get_values()
        with_user = self.env['ir.config_parameter'].sudo()
        profile_email_ids = with_user.get_param(
            'many2many.profile_email_ids')
        
        res.update(
            profile_email_ids=[(6, 0, literal_eval(profile_email_ids))]
            if profile_email_ids else False)
        
        return res