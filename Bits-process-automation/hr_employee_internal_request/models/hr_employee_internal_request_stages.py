# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrEmployeeInternalRequestStages(models.Model):
    _name = 'hr.employee.internal.request.stages'

    name = fields.Char(
        _('Stage Name'),
        required=True,
        translate=True)
    sequence = fields.Integer(
        _('Sequence'),
        default=1,
        help="Used to order stages. Lower is first.")
    close = fields.Boolean(
        _('Closing Stage'),
        help=_('When is checked this stage are considered as done.\
            This is used when flow is finished'))
    email_profile_ids = fields.Many2many(
        'hr.job',
        'hr_job_employee_request_stages',
        string='Email per profile')
    template_id = fields.Many2one(
        'mail.template', 'Email Template',
        domain="[('model', '=', 'hr.employee.internal.request')]",
        help="Automated email sending to assigned jobs at this stage")
    is_cancelled = fields.Boolean(
        "cancellation stage")
