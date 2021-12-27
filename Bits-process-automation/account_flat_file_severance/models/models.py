# -*- coding: utf-8 -*-

from odoo import models, fields, api


class model(models.Model):
    _name = 'account_flat_file_severance.account_flat_file_severance'
    _description = 'account_flat_file_severance.account_flat_file_severance'

    name = fields.Char()
    document_type = fields.Selection([
        ('12', "Identity card"),
        ('13', "Citizenship card"),
        ('22', 'Foreigner ID'),
        ('41', 'Passport'),
        ('OT', 'Others')
    ], string="Document type", required=True, default='13')
    document_number = fields.Char('Identification No')
    first_name = fields.Char('First name')
    second_name = fields.Char('Second name')
    surname = fields.Char('Surname')
    second_surname = fields.Char('Second surname')
    wage = fields.Float(digits=(32, 2), string='Wage')
    layoffs = fields.Float(digits=(32, 2), string="layoffs value")
    worked_days = fields.Integer('Worked days')
    phone = fields.Char('Phone')
    address = fields.Char('Address')
    email = fields.Char('Email address')
    # company_id = fields.Many2one('res.company',
    #                              default=lambda self: self.env.company,
    #                              required=True)
