# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountFormatExogenus(models.Model):
    _name = 'account.format.exogenus'

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True, size=8)
    format_type = fields.Selection(selection=[
        ('dian', 'DIAN'), ('district', 'District')], string="Type",
        required=True)
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.company)
    partner_report = fields.Boolean(string="Partner Report", default=False)
    description = fields.Char(string="Description")
    account_column_ids = fields.One2many(
        'account.exogenus.format.column',
        'account_format_id',
        string="Account column configuration")
    bool_concept = fields.Boolean(string="Have concept")
    bool_lesser_amount = fields.Boolean(string="Have Lesser Amount")
    bool_amount = fields.Boolean(string="Amount Tax")

    _sql_constraints = [
        ('unique_code_format_exogenus',
         'unique (code)',
         'You cannot create more than one format with the same code')
    ]

    @api.constrains('account_column_ids')
    def _check_exist_record_in_lines(self):
        for rec in self:
            exis_record_lines = []
            for line in rec.account_column_ids:
                if line.account_column_id.id in exis_record_lines:
                    raise ValidationError(
                        _('The column should be one per line'))
                exis_record_lines.append(line.account_column_id.id)
