# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountConceptExogenus(models.Model):
    _name = 'account.concept.exogenus'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', size=8)
    format_exogenus_id = fields.Many2one(
        'account.format.exogenus', string="Format Exogenus", required=True)
    format_exogenus_code = fields.Char(string="Code Format", size=8)
    concept_exogenus_line_ids = fields.One2many(
        'account.concept.exogenus.line', 'concept_exogenus_id',
        string="Concept Lines")
    concept_code = fields.Boolean(string="Code Concept", default=True)
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency',
                                  related='company_id.currency_id',
                                  readonly=True)
    partner_report = fields.Boolean(
        string="Partner Report",
        related="format_exogenus_id.partner_report")

    # Members Report
    fiscal_liquid_equity = fields.Monetary(
        string="Fiscal Liquid Equity",
        help="Tax net equity as of December 31 of the year to be reported")
    joint_stock_company = fields.Boolean(string="Join Stock Company")
    number_shares_outstanding = fields.Float(
        string="Number Shares Outstanding",
        help=("If it is a joint stock company, "
              "indicate the number of shares in circulation"))
    base_amounts_report = fields.Monetary(string="Base Amounts to Report")
    partners_shareholders_line_ids = fields.One2many(
        'partners.shareholders.lines', 'concept_exogenus_id',
        string="Concept Lines")
    total_percentage = fields.Float(
        string="Total Percentage")
    total_number_share = fields.Float(
        string="Total Percentage")
    account_account_ids = fields.Many2many(
        'account.account',
        string="Accounts")
    lesser_amount = fields.Float(string='Lesser Amount')


class AccountConceptExogenusLine(models.Model):
    _name = 'account.concept.exogenus.line'

    name = fields.Char(string='Name', required=True,
                       related="concept_exogenus_id.code")
    concept_exogenus_id = fields.Many2one(
        'account.concept.exogenus', string='Concept',
        ondelete="cascade", index=True, auto_join=True, store=True)
    account_id = fields.Many2one(
        'account.account', string="Account")
    account_code = fields.Char(
        string="Account Code", related="account_id.code")
    lesser_amount = fields.Float(
        string='Lesser Amount',
        related="concept_exogenus_id.lesser_amount", store=True)
    deductible = fields.Boolean(string="Deductible")
    deducible_percentage = fields.Float(string="Deducible Percentage")
    account_cost_expense_deductible_id = fields.Many2one(
        'account.account',
        string='IVA Account Costo or Expense Deductible')
    account_cost_expense_not_deductible_id = fields.Many2one(
        'account.account',
        string='IVA Account Costo or Expense Not Deductible')
    account_witholding_source_id = fields.Many2one(
        'account.account', string="Account Withholding Source")
    account_withholding_assumed_income_id = fields.Many2one(
        'account.account',
        string="Account Withholding Tax Assumed for Income")
    account_iva_withholding_common_regime_id = fields.Many2one(
        'account.account', string="IVA Withholding Account to Common Regime")
    account_non_domiciled_iva_Withholding_id = fields.Many2one(
        'account.account', string="Non-domiciled VAT Withholding Account")
    company_id = fields.Many2one('res.company',
                                 default=lambda self: self.env.company)

    @api.constrains('deducible_percentage')
    def _check_deducible_percentage(self):
        for record in self:
            if record.deducible_percentage > 100:
                raise ValidationError(_(
                    'The percentage cannot be greater than 100'))


class PartnerShareholdersLiness(models.Model):
    _name = 'partners.shareholders.lines'

    name = fields.Char(string="Name", required=True,
                       related="concept_exogenus_id.code")
    concept_exogenus_id = fields.Many2one(
        'account.concept.exogenus', string='Concept', required=True,
        ondelete="cascade", index=True, auto_join=True)
    partner_id = fields.Many2one('res.partner', required=True)
    number_share = fields.Float(string="Number Share", required=True)
    participation_percentage = fields.Float(
        string="Participation Percentage",
        compute="_compute_participation_percentage")
