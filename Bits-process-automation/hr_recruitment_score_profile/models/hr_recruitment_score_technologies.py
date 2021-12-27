# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class HrRecruitmentScoreTechnologies(models.Model):

    _name = "hr.recruitment.score.technologies" # Nuevo modelo en la base de datos
    _description = "Technologies"               # Descripción del nuevo modelo(tecnologias)

    name = fields.Char(string='Name',tracking=True) #campo para digitar el nombre de la tecnologia
    code = fields.Char(string='Code',tracking=True,readonly=True, required=True, copy=False, default='New') #campo para digitar el codigo
    active = fields.Boolean(string='Active',tracking=True) #campo para activar la opcion(True)
    description = fields.Char(string='Description',tracking=True) #campo para colocar la descripcion de la tecnologia
    skill_id = fields.Many2one('hr.recruitment.score.skills') #campo para seleccionar una habilidad


    # Ejecutar Secuencia 
    @api.model
    def create(self, vals):
        if vals.get('code', 'New') == 'New':
            vals['code'] = self.env['ir.sequence'].next_by_code('score.tecnology') or 'New'
        result = super(HrRecruitmentScoreTechnologies, self).create(vals)
        return result