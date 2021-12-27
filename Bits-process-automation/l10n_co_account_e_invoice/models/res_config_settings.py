# coding: utf-8
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    template_code = fields.Selection(
        string="Colombia Template Code",
        readonly=False,
        related="company_id.template_code")

    active_tech_provider = fields.Boolean(
        readonly=False,
        related="company_id.active_tech_provider"
    )

    module_l10n_co_sequence_resolution = fields.Boolean(
        string='Integrate resolutions',
    )

    def l10n_co_install_group_taxes(self):
        self.env['account.tax.template']._configure_l10n_co_account_tax_data(
            self.company_id
        )

    sale_tax_ids = fields.Many2many(
        'account.tax',
        string="Default Sale Tax",
        related='company_id.account_sale_tax_ids',
        readonly=False
    )

    tax_group_id = fields.Many2one(
        readonly=False,
        related="company_id.tax_group_id"
    )

    type_documents_for_invoice = fields.Many2many(
        'l10n_co.type_documents',
        string="Types of Documents for Invoice",
        related="company_id.account_type_documents_for_invoice",
        readonly=False
    )

    type_documents_for_credit_note = fields.Many2many(
        'l10n_co.type_documents',
        string="Types of Documents for Credit Note",
        related="company_id.account_type_documents_for_credit_note",
        readonly=False
    )

    type_documents_for_debit_note = fields.Many2many(
        'l10n_co.type_documents',
        string="Types of Documents for Debit Note",
        related="company_id.account_type_documents_for_debit_note",
        readonly=False
    )
