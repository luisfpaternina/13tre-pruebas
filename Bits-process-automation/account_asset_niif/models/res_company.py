from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = "res.company"

    loss_account_colgap_id = fields.Many2one(
        'account.account',
        domain="[('deprecated', '=', False), ('company_id', '=', id)]",
        help="Account used to write the journal item in case of loss," +
             " COLGAP accounting")
