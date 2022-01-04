# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

import string
import random

class CallRegister(models.Model):
    _name = 'call.register'
    _description = "Call Register"
    _rec_name = 'from_number'

    start_date = fields.Datetime(string='Start Time')
    answered_time = fields.Datetime(string='Answered Time')
    call_end = fields.Datetime(string='End Time')
    incall_duration = fields.Integer(string='Incall Duration (sec)')
    total_duration = fields.Integer(string='Total Duration (sec)')
    user_id = fields.Many2one('res.users', string='User', required=False)
    partner_id = fields.Many2one('res.partner', string='Contact', required=False)
    direction = fields.Selection([('in', 'In'), ('out', 'Out')], string="Direction")
    last_state = fields.Char(string='Last State')
    type = fields.Char(string="Type")
    from_number = fields.Char('From number')
    to_number = fields.Char('To number')
    contact_number = fields.Char('Contact number')
    call_id = fields.Char(string="Call id")
    cdr_id = fields.Integer(string="CDR id")
    active = fields.Boolean(default=True)
