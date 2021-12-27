# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError


class DocumentVersionControl(models.Model):
    _name = 'document.version.control'

    name = fields.Char('Document Name')
    model_id = fields.Many2one('ir.model', 'Model')
    res_id = fields.Integer(
        string='Record'
    )
    version = fields.Char(
        string='Version',
    )
    description = fields.Char(
        string='Discription',
    )
    version_date = fields.Date(
        string='Version Date',
        default=fields.Date.context_today,
    )
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)','field would be unique!')
    ]
