# -*- coding: utf-8 -*-
from odoo import models, fields, api


class IndustrialClassification(models.Model):
    _name = 'ciiu'
    _description = 'ISIC List'

    name = fields.Char(
        string='Code and Description',
        store=True,
        compute='_compute_concat_name'
    )
    code = fields.Char(required=True)
    description = fields.Char(required=True)
    type = fields.Char(
        store=True,
        compute='_compute_set_type'
    )
    has_parent = fields.Boolean('Has Parent?')
    parent = fields.Many2one('ciiu', 'Parent')

    has_division = fields.Boolean('Has Division?')
    division = fields.Many2one('ciiu', 'Division')

    has_section = fields.Boolean('Has Section?')
    section = fields.Many2one('ciiu', 'Section')

    hierarchy = fields.Selection([
        ('1', 'Has Parent?'),
        ('2', 'Has Division?'),
        ('3', 'Has Section?')],
    )

    @api.depends('code', 'description')
    def _compute_concat_name(self):
        for rec in self:
            rec.name = (rec.code.strip() + ' - ' + rec.description.strip())

    @api.depends('has_parent')
    def _compute_set_type(self):
        for rec in self:
            rec.type = 'view' if not rec.has_parent else 'view' \
                if (rec.division or rec.section) else 'other'
