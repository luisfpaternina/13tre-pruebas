from odoo import models, fields, api, _

class ResCompany(models.Model):
    _inherit = 'res.company'

    terms = fields.Text(
        string="Terms")
    picking_terms = fields.Text(
        string="Picking terms")
    purchase_terms = fields.Text(
        string="Purchase terms")
    sale_terms = fields.Text(
        string="Sale terms")
