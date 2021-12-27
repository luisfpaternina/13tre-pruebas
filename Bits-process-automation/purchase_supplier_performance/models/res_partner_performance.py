from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResPartnerPerformance(models.Model):
    _name = 'res.partner.performance'

    def _get_default_user(self):
        return self.env.user.id

    def _get_default_company(self):
        return self.env.company.id

    name = fields.Char(
        string='Name', related="partner_id.display_name", store=True)
    partner_id = fields.Many2one(
        string='Partner', comodel_name='res.partner', required=True)
    performance = fields.Selection(string='Performance', selection=[
        ('0', 'Very Bad'), ('1', 'Bad'), ('2', 'Regular'), ('3', 'Good')],
        default='0'
    )
    description = fields.Char(string='Description')
    type = fields.Selection(string='Type',
                            selection=[('supplier', 'Supplier')],
                            required=True)
    qualification_date = fields.Date(
        string="Qualification Date", default=fields.Date.today())
    user_id = fields.Many2one(
        'res.users', 'User Qualification', default=_get_default_user)

    order_id = fields.Many2one('purchase.order', 'Purchase Order')
    company_id = fields.Many2one(
        'res.company', 'Company', index=True,
        default=_get_default_company)
