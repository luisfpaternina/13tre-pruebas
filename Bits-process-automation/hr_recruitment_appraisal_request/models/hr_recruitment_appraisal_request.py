# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class HrRecruitmentAppraisalRequest(models.Model):
    _name = 'hr.recruitment.appraisal.request'
    _description = 'Internal appraisal'
    
    name = fields.Char(string="Name")
    employee_id = fields.Many2one('hr.employee', string="Evaluator")
    
    


    

  
  