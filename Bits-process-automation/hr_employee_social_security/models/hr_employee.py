# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrEmployeeSocialSecurity(models.Model):
    _inherit = 'hr.employee'

    arl = fields.Many2one(
        "social.security",
        string="Arl")
    health = fields.Many2one(
        'social.security',
        string="Eps")
    pension = fields.Many2one(
        'social.security',
        string="Pension")
    layoffs = fields.Many2one(
        'social.security', ondelete="cascade", index=True,
        string="Layoffs"
    )
    compensation_box = fields.Many2one(
        'social.security',
        string="Compensation Box")
    contributor_type = fields.Many2one(
        'social.security',
        string="Contributor Type", compute="_compute_contributor_type")
    contributor_subtype = fields.Many2one(
        'social.security',
        string="Contributor Subtype")

    # Fields Contract
    contract_id = fields.Many2one(
        'hr.contract',
        ondelete="cascade",
        index=True,
        string="Contract"
    )

    risk_class = fields.Char(
        string='Risk Class',
        related='contract_id.risk_class.name'
    )

    rate = fields.Float(
        string="Rate",
        related="contract_id.rate"
    )

    def _compute_contributor_type(self):
        for record in self:
            if record.contract_ids:
                record.contributor_type = record.contract_ids[-1].contributor_type_id
                break

            else:
                record.contributor_type = False