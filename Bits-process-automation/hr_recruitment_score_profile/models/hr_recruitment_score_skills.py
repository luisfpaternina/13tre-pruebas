# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)

class HrRecruitmentScoreSkills(models.Model):

    _name = "hr.recruitment.score.skills"  # Nuevo modelo(tabla) en la base de datos
    _description = "Skillis"               # descripción del modelo(habilidades)

    name = fields.Char(string='Name',tracking=True) #campo para colocar el nombre de la habilidad
    code = fields.Char(string='Code',tracking=True,readonly=True, required=True, copy=False, default='New') #campo para digitar el codigo de la habilidad
    active = fields.Boolean(string='Active',tracking=True) #campo boleano para activar(True)
    description = fields.Char(string='Description',tracking=True) #campo para colocar la descricion de la habilidad
    percentage = fields.Float(string="% Percentage") #campo para colocar el porcentaje
    technology_id = fields.Many2one('hr.recruitment.score.technologies', string="Technology") #campo para seleccionar la tecnologia
    total_items = fields.Integer(string="Total items")
    profile_id = fields.Many2one('hr.recruitment.score.profile', string="Profile")
    

    # Ejecutar Secuencia 
    @api.model
    def create(self, vals):
        if vals.get('code', 'New') == 'New':
            vals['code'] = self.env['ir.sequence'].next_by_code('score.skills') or 'New'
        result = super(HrRecruitmentScoreSkills, self).create(vals)
        return result

        
class HrRecruitmentScoreLinesSkills(models.Model):

    _name = "hr.recruitment.score.lines.skills"  # Nuevo modelo(tabla) en la base de datos
    _description = "Lines Skillis"               # descripción del modelo(Lineas de las habilidades)

    #############################################################################
    #                                  CAMPOS
    #############################################################################
    skill_id = fields.Many2one('hr.recruitment.score.skills', string="Skill") #campo para seleccionar la habilidad
    profile_id = fields.Many2one('hr.recruitment.score.profile', string="Profile")
    

    




    
    
