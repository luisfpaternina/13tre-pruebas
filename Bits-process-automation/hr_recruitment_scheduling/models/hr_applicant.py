# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    def action_makeMeeting(self):
        res = super(HrApplicant, self).action_makeMeeting()

        assigned_to = self.stage_id.assigned_to

        if assigned_to:
            res['context']['default_partner_ids'].append(assigned_to.id)

        return res

    @api.model
    def create(self, values):
        new_partner = self.env['res.partner'].create({
            'name': values.get('email_from'),
            'email': values.get('email_from')
        })

        values['partner_id'] = new_partner.id

        return super(HrApplicant, self).create(values)
