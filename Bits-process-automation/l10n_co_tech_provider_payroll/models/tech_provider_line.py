# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TechProviderLine(models.Model):
    _name = 'l10n_co.tech.provider.line'
    _inherit = 'l10n_co.tech.provider.line'

    cardinality = fields.Selection(selection=[('0_1','0-1'), ('0_n','0-N'), ('1_1','1-1'), ('1_n','1-N'),('setting','Ajuste')], string="Cardinality")