# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrRecruitmentLanguage(models.Model):
    _name = 'hr.recruitment.language'
    _description = _('Recruitment language aptitudes configuration')

    hr_job = fields.Many2one(
        'hr.job'
    )
    language = fields.Many2one(
        'res.lang',
        _('Language'),
        required=True)
    reading = fields.Many2one(
        'hr.recruitment.level',
        string=_('Reading')
    )
    writing = fields.Many2one(
        'hr.recruitment.level',
        string=_('Writing')
    )
    speaking = fields.Many2one(
        'hr.recruitment.level',
        string=_('Speaking')
    )
    listening = fields.Many2one(
        'hr.recruitment.level',
        string=_('Listening')
    )
