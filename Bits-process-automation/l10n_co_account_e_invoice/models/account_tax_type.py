# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AccountTaxType(models.Model):
    _name = 'account.tax.type'
    _description = (
        'Management of tax rates for Colombian electronic invoicing'
    )

    code = fields.Char(required=True)
    name = fields.Char(required=True)
    retention = fields.Boolean()
    count_tax = fields.Integer(compute="get_count_tax")

    def get_count_tax(self):
        for record in self:
            record.count_tax = (
                self.env['account.tax'].search_count(
                    [
                        ('type_of_tax', '=', self.id)
                    ]
                )
            )

    def get_tax(self):
        self.ensure_one()
        views = [
            (self.env.ref('account.view_tax_tree').id, 'tree'),
            (self.env.ref('account.view_tax_form').id, 'form')
        ]
        return {
            'type': 'ir.actions.act_window',
            'name': 'Taxes',
            'view_mode': 'tree,form',
            'views': views,
            'res_model': 'account.tax',
            'domain': [('type_of_tax', '=', self.id)],
            'context': "{'create': False}",
        }
