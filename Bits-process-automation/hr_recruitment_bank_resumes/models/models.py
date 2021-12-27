# -*- coding: utf-8 -*-

import re
from odoo.exceptions import ValidationError

from odoo import models, fields, api, _


class hr_recruitment_bank_resumes(models.Model):
    _name = 'hr.recruitment.bank.resumes'
    _inherit = ['mail.activity.mixin', 'mail.thread.cc']
    _description = _('Show list of candidates for someone vacant')

    name = fields.Char(required=True, string=_('name'))  # nombre
    vacant = fields.Many2one(
        'hr.job',
        string=_('vacant'),
        required=True
    )  # vacante "hr.job"

    email = fields.Char(string=_('email'), size=60)

    contact_phone = fields.Char(string=_('contact_phone'))

    linkedin = fields.Char(string=_('linkedin'))  # linkedin
    laboral_experience = fields.Selection([
        ('without_exp', 'Sin experiencia laboral'),
        ('min_year', 'Menos de un (1) año'),
        ('2_to_4_years', 'De 2 a 4 años'),
        ('4_to_6_years', 'De 4 a 6 años'),
        ('more_6_years', 'Más de 6 años')
    ], string=_('laboral_experience'), required=True)  # experiencia Laboral
    english_level = fields.Selection([
        ('low', 'Bajo'),
        ('medium', 'Medio'),
        ('high', 'Alto'),
    ], string=_('english_level'), required=True)  # nivel de Ingles
    studies = fields.Selection([
        ('technician', 'Técnico'),
        ('technologist', 'Tecnólogo'),
        ('professional', 'Profesional'),
        ('postgraduate', 'Posgrado')
    ], string=_('studies'), required=True)  # estudios
    salary_aspiration = fields.Float(
        digits=(32, 2),
        string=_('salary_aspiration'))  # aspiración Salarial "float"
    # tecnologías TODO "multiple option"
    technologies = fields.Selection([
        ('net', '. Net'),
        ('odoo', 'Odoo'),
        ('python', 'Python'),
        ('php', 'PHP'),
        ('javascript', 'Javascript'),
        ('ionic', 'Ionic')
    ], string=_('technologies'), required=True)

    # disponibilidad TODO "selection field" manyToMany
    availability = fields.Char(string=_('availability'))

    @api.constrains('email', 'contact_phone')
    def _validate_data(self):
        if self.email:
            re_validate_email = re.compile(
                r'^[_a-z0-9-]+(\.[_a-z0-9-]+)'
                r'*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$'
            )
            validate_email = re.match(
                re_validate_email,
                self.email)
            if validate_email is None:
                raise ValidationError(
                    _(
                        "It's not a valid format email for:"
                        'email'
                    )
                )

        if self.contact_phone:
            re_validate_contact_phone = re.compile(
                r'\d{7,13}$'
            )
            validate_contact_phone = re.match(
                re_validate_contact_phone,
                self.contact_phone)
            if validate_contact_phone is None:
                raise ValidationError(
                    _(
                        "It's not a valid format contact phone for:"
                        'contact_phone'
                    )
                )
