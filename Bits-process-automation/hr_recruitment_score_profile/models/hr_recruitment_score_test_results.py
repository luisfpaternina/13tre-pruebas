# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
import math

_logger = logging.getLogger(__name__)

class HrRecruitmentScoreTestResults(models.Model):

    _name = "hr.recruitment.score.test.results" # nuevo modelo(tabla) en la base de datos
    _description = "Test results" # Descripción del modelo(perfiles)
    _rec_name = 'applicant_id' #atributo para el arbol de busqueda del modelo

    tecnology_id = fields.Many2one('hr.recruitment.score.technologies', string="Tecnology")
    skills = fields.Many2one('hr.recruitment.score.skills', string="Skills")
    test_result = fields.Float(string="Test result")
    applicant_id = fields.Many2one('hr.applicant', string="Applicant postulation")
    test_result_lines = fields.One2many('hr.recruitment.score.test.results.lines','result_id','Results applicant lines')
    calculated_total = fields.Float(string="Calculated Total", store=True)
    weighted_average = fields.Float(string="Weighted average", store=True)
    total_items = fields.Integer(string="Total items", store=True)
    mjs = fields.Char(string="Msj", store=True)
    profile_id = fields.Many2one('hr.recruitment.score.profile', string="job profile")


    @api.onchange('weighted_average','tecnology_id')
    def _onchange_mjs(self):
        list_average = []
        ids_profile = []
        order_t = []
        tupla = []
        profile_obj = self.env['hr.recruitment.score.profile'].search([('tecnology_id','=',self.tecnology_id.id)])
        
        for line_profile in profile_obj:
            list_average.append(line_profile.weighted_average_related)
            ids_profile.append(line_profile.id)
            tupla = tuple(zip(ids_profile, list_average))
        
        for t in tupla:
            order_t.append(t)
        
        for line_t in order_t:
            if self.weighted_average >= line_t[1]:
                profile_found = self.env['hr.recruitment.score.profile'].search([('id','=',line_t[0])])
                self.mjs = profile_found.name
            
            elif self.weighted_average <= 0:
                self.mjs = 'Perfil no creado en el sistema'
        
       
    @api.onchange('test_result_lines')
    def compute_test_result_lines(self):
        if self.test_result_lines:
            self.total_items = len(self.test_result_lines)
        else:
            print("No hay lineas")
            self.total_items = False


    @api.onchange('test_result_lines')
    def _calculated_weighted_average(self):
        for record in self:
            if record.total_items:
                record.weighted_average = (record.calculated_total) / (float(record.total_items))
            else:
                record.weighted_average = 0.0 
           

    @api.onchange('test_result_lines')
    def _calculated_total(self):
        sum = 0
        for line in self.test_result_lines:
            sum = line.percentage + sum
        
        self.calculated_total = sum
                

class HrRecruitmentScoreTestLines(models.Model):

    _name = "hr.recruitment.score.test.results.lines" # heredar  modelo(tabla) en la base de datos
    _description = "Test results lines" # Descripción del modelo(perfiles)

    result_id = fields.Many2one('hr.recruitment.score.test.results', string="Applicant")
    skill_id = fields.Many2one('hr.recruitment.score.skills', string="Skills")
    percentage = fields.Float(string="% Percentage")
    margen=fields.Float(related="percentage", string="%")