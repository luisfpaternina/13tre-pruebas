# -*- coding: utf-8 -*-

from typing import DefaultDict
from odoo import models, fields, api, _


class SocialSecurity(models.Model):

    _name = 'social.security'
    _description = 'HR employee social security'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Name')
    entity_type = fields.Selection(
        [
            ('health', 'Eps'),
            ('pension', 'Pension'),
            ('arl', 'Arl'),
            ('layoffs', 'Layoffs'),
            ('compensation_box', 'Compensation Box'),
            ('contributor_type', 'Contributor Type'),
            ('contributor_subtype', 'Contributor Subtype'),
            ('risk_class', 'Risk Class')
        ],
        string="Type"
    )
    active = fields.Boolean('Active', default=True)
