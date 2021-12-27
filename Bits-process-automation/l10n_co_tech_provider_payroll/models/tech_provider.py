# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TechProvider(models.Model):
    _inherit = 'l10n_co.tech.provider'

    active = fields.Boolean(default=True)
    _type = fields.Selection(selection_add=[('payroll', 'Payroll')])

    def action_test_connection(self):
        res = super(TechProvider, self).action_test_connection()
        if self._type != 'payroll':
            return res
        else:
            return True