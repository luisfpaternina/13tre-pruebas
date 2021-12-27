# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'
    _description = 'Applicants'
    
    internal_request_id = fields.Many2one('hr.recruitment.internal.request', string="Internal request")

   