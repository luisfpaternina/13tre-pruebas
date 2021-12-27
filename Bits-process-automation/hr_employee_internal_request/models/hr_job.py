# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class Job(models.Model):
    _inherit = "hr.job"

    internal_request_count = fields.Integer(
        compute='_compute_internal_request_count',
        string="Internal Request Count")

    internal_request_ids = fields.One2many(
        'hr.employee.internal.request', 'job_position', 'Internal Requests')

    def _compute_internal_request_count(self):
        quantity = self.env["hr.employee.internal.request"].search([
            ("job_position.id", "=", self.id)
        ])
        count = 0
        for request in quantity:
            count += 1
        self.internal_request_count = count
        
    def action_get_internal_request_tree_view(self):
        return False
