# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from werkzeug.urls import url_join


class HrEmployeeInternalRequest(models.Model):
    _inherit = 'hr.employee.internal.request'

    applicant_line_ids = fields.One2many(
        'hr.applicant',
        'internal_request',
        string="Applicant Lines"
    )
