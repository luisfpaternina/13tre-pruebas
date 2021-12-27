# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class HrRecruitmentScoreProfile(models.Model):

    _name = "hr.recruitment.score.profile" # nuevo modelo(tabla) en la base de datos
    _description = "Profiles"              # Descripción del modelo(perfiles)

    name = fields.Char(string='Name',tracking=True) #campo para digitar el nombre del perfil
    code = fields.Char(string='Code',tracking=True,readonly=True, required=True, copy=False, default='New') #campo para digitar el codigo del perfil
    active = fields.Boolean(string='Active',tracking=True) #campo para activar el perfil(True)
    description = fields.Char(string='Description',tracking=True) #campo para colocar la descripcion del perfil
    percentage = fields.Float(string="% Percentage") #campo para digitar el porcentaje
    profile_line_ids = fields.One2many('hr.recruitment.score.profile.lines','profile_id','profile lines')
    tecnology_id = fields.Many2one("hr.recruitment.score.technologies", string="Tecnology")
    calculated_total = fields.Float(string="Calculated Total", compute="_calculated_total")
    weighted_average = fields.Float(string="Weighted average")
    total_items = fields.Integer(string="Total items", compute="compute_test_result_lines")
    weighted_average_related = fields.Float(string="Weighted average", store=True)
    
    
    #Ejecutar Secuencia 
    @api.model
    def create(self, vals):
        if vals.get('code', 'New') == 'New':
            vals['code'] = self.env['ir.sequence'].next_by_code('score.profile') or 'New'
        result = super(HrRecruitmentScoreProfile, self).create(vals)
        return result


    @api.depends('profile_line_ids')
    def compute_test_result_lines(self):
        if self.profile_line_ids:
            self.total_items = len(self.profile_line_ids)
        else:
            print("No hay lineas en el perfil")
            self.total_items = len(self.profile_line_ids)

   
    @api.onchange('profile_line_ids')
    def _calculated_weighted_average_related(self):
        porcentajes= []
        for record in self.profile_line_ids:
            porcentajes.append(record.percentage)
        
        if porcentajes:
            _logger.info(sum(porcentajes)/len(porcentajes))
            self.weighted_average_related = sum(porcentajes)/len(porcentajes)
        else:
            self.weighted_average_related = 0.0
       
        
    @api.depends('profile_line_ids')
    def _calculated_total(self):
        for record in self:
            for line in record.profile_line_ids:
                if record.profile_line_ids and record.total_items > 0:
                    record.calculated_total += line.percentage
                else:
                    record.calculated_total = 0.0
            record.calculated_total = 0.0
    


class HrRecruitmentScoreProfileLines(models.Model):

    _name = "hr.recruitment.score.profile.lines" # heredar  modelo(tabla) en la base de datos
    _description = "Profiles lines" # Descripción del modelo(perfiles)

    skill_id = fields.Many2one('hr.recruitment.score.skills', string="Skills")
    percentage = fields.Float(string="% Percentage")
    margen=fields.Float(related="percentage", string="%")
    profile_id = fields.Many2one('hr.recruitment.score.profile', string="Profile") #campo para seleccionar el perfil