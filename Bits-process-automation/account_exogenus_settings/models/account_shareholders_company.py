# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountShareholdersCompany(models.Model):
    _name = 'account.shareholders.company'

    name = fields.Char(
        string="Name",
        required=True
    )
    year = fields.Integer(
        string='Year',
        size=4,
        required=True
    )
    liquid_assets = fields.Float(
        string="Liquid Assets",
        required=True
    )
    total_number_shares = fields.Float(
        string="Total Number of Shares",
        required=True
    )
    smaller_amounts = fields.Float(
        string="Smaller Amounts"
    )
    account_shareholders_company_line_ids = fields.One2many(
        "account.shareholders.company.line",
        "account_shareholders_company_id",
        string="Shareholders"
    )

    @api.onchange('account_shareholders_company_line_ids')
    def onchange_number_shares(self):
        for record in self:
            self.validate_number_of_shares(record)

    @api.onchange('total_number_shares')
    def validate_number_of_shares(self, record=False):
        record = record if record else self
        total_number_shares = 0
        if record.total_number_shares:
            for line in record.account_shareholders_company_line_ids:
                line.percentage_share = \
                    line.number_shares * 100 / \
                    record.total_number_shares
                total_number_shares += line.number_shares

            if total_number_shares > record.total_number_shares:
                raise ValidationError(
                    _('The sum of number of shares per shareholder must '
                        'not exceed the total number of shares.'))
        else:
            raise ValidationError(
                _('A value in total number of shares must be assigned.'))


class AccountShareholdersCompanyLine(models.Model):
    _name = 'account.shareholders.company.line'

    partner_id = fields.Many2one(
        "res.partner",
        string="Shareholder",
        required=True
    )
    number_shares = fields.Float(
        string="Number of Shares",
        required=True
    )
    percentage_share = fields.Float(
        string="Percentage Share"
    )
    shareholder_contribution = fields.Float(
        string="Shareholder Contribution",
        compute="_calc_shareholder_contribution",
        store=True
    )
    account_shareholders_company_id = fields.Many2one(
        "account.shareholders.company",
        string="Account Shareholders Company"
    )

    @api.depends(
        'account_shareholders_company_id.liquid_assets', 'percentage_share')
    def _calc_shareholder_contribution(self):
        for record in self:
            record.shareholder_contribution =\
                record.account_shareholders_company_id.liquid_assets \
                * (record.percentage_share / 100)

    def create(self, vals):
        for line in vals:
            if line.get("number_shares", False) == 0:
                raise ValidationError(
                    _('The number of shares must not be zero.'))
        return super(AccountShareholdersCompanyLine, self).create(vals)

    def write(self, vals):
        if vals.get("number_shares", 'False') != 'False'\
                and vals.get("number_shares", False) == 0:
            raise ValidationError(
                _('The number of shares must not be zero.'))
        return super(AccountShareholdersCompanyLine, self).write(vals)
