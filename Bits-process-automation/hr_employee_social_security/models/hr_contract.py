# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class InheritanceEmployee(models.Model):

    _inherit = "hr.contract"

    risk_class = fields.Many2one(
        'social.security',
        domain="[('entity_type', '=', 'risk_class')]",
        string="Risk Class",
        required=True)

    # This is the field 'Tarifa'
    rate = fields.Float(
        string="Rate",
        digits='Payroll Rate')

    pension_special_rate_indicator = fields.Selection([
        (' ', 'normal rate'),
        ('1', 'High risk activities'),
        ('2', 'Senators'),
        ('3', 'CTI'),
        ('4', 'Airmen'),
    ], default=' ', string="Pension Special Rate Indicator")

    pensions_contrib = fields.Boolean(
        default=False,
        string="Foreigner Not Obliged Contribute Pensions")

    colombian_abroad = fields.Boolean(
        default=False,
        string="Colombian Abroad")

    @api.onchange('risk_class')
    def _onchange_risk_class(self):
        self.ensure_one()
        dict_rate = {
            '0': 0,
            '1': 0.522,
            '2': 1.044,
            '3': 2.436,
            '4': 4.350,
            '5': 6.960,
        }

        new_rate = (
            dict_rate.get(
                f"{self.risk_class.code}", 0))

        self.write({'rate': new_rate})
