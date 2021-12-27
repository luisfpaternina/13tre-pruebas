# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrJob(models.Model):
    _inherit = 'hr.job'

    dependants = fields.Boolean(
        string=_('Dependants'))
    vocational_training = fields.Many2one(
        'res.partner.title',
        string=_('Vocational Training'))
    general_experience = fields.Many2one(
        'hr.recruitment.experience',
        string=_('General Experience'))
    specific_experience = fields.Many2one(
        'hr.recruitment.experience',
        string=_('Specific Experience'))
    language_ids = fields.One2many(
        'hr.recruitment.language',
        'hr_job',
        string=_('Language'))
    job_objectives = fields.Text(
        string=_('Job Objectives'))
    supervision = fields.Many2one(
        'hr.job',
        string=_('Supervision'))
    job_functions = fields.Text(
        string=_('Job Functions'))
    # Crear tabla relacional para responsabilidades (Texto)
    job_responsibilities = fields.Text(
        string=_('Job Responsibilities'))
    replaces_to = fields.Many2one(
        'hr.job',
        string=_('Replaces To'))
    replaced_by = fields.Many2one(
        'hr.job',
        string=_('Replaced By'))
    software = fields.Text(
        string=_('Software'))
    hardware = fields.Text(
        string=_('Hardware'))
    additional_elements = fields.Text(
        string=_('Additional Elements'))
    # Crear tabla relacional sst (Texto)
    partners_sst_responsibilities = fields.Text(
        string=_('Partners SST Responsibilities'))
    # Crear tabla relacional sst (Texto)
    sst_responsibilities_with_dependants = fields.Text(
        string=_('Job Responsibilities with dependants'))

    organizational_competencies_ids = fields.One2many(
        'hr.recruitment.has.organizational.competencies',
        'charge_id',
        string=_('Organizational Competencies')
    )

    positions_charge_competencies_ids = fields.One2many(
        'hr.recruitment.has.positions.in.charge.competencies',
        'charge_id',
        string=_('Charge Competencies'))

    responsabilities_charge_ids = fields.One2many(
        'hr.recruitment.has.responsabilities.charge',
        'charge_id',
        string=_('Responsabilities Charge'))

    technical_technological_competencies_ids = fields.One2many(
        'hr.recruitment.has.technical.technological.competencies',
        'charge_id',
        string=_('Technical Technological Competencies'))

    specific_competencies_ids = fields.One2many(
        'hr.recruitment.has.specific.competencies',
        'charge_id',
        string=_('Specific Competencies'))
