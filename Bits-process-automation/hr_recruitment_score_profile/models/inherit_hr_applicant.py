# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class HrApplicant(models.Model):

    _inherit = "hr.applicant" # heredar  modelo(tabla) en la base de datos
    _description = "Applicant" # Descripción del modelo(perfiles)

    test_result_count = fields.Integer(string="test result count", compute="_compute_test_result_count")
    test_result_ids = fields.One2many('hr.recruitment.score.test.results', 'applicant_id', 'Test results count')
    
    
    #contador
    def _compute_test_result_count(self):
        for record in self:
            count = len(record.test_result_ids)
            record.test_result_count = count


class HrApplicantLines(models.Model):

    _name = "hr.applicant.lines" # heredar  modelo(tabla) en la base de datos
    _description = "Applicant lines" # Descripción del modelo(perfiles)