# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class HrRecruitmentInternalRequest(models.Model):
    _name = 'hr.recruitment.internal.request'
    _description = 'Internal request'
    
    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    job_id = fields.Many2one('hr.job', string="Job")
    department_id = fields.Many2one('hr.department', string="Department")
    numbers_of_employees = fields.Integer(string="Employee's Numbers")
    analytic_account_id = fields.Many2one('account.analytic.account',string="Analytic account")
    customers_own_request = fields.Boolean(string="customer's own request")
    description = fields.Text(string="Description")
    
    

class HrRecruitmentInternalRequestSurveys(models.Model):
    _name = 'hr.recruitment.internal.request.survey'
    _description = 'Internal request surveys'
    

  
  