from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class HrPayrollUvtRange(models.Model):
    _name = 'hr.payroll.uvt.range'

    name = fields.Char(string="name")
    percentage = fields.Integer(string="Percentage")
    uvt_quantity = fields.Integer(string="Uvt Quantity")
    uvt_amount_subtract = fields.Integer(string="Uvt Amount Subtract")
    uvt_amount_add = fields.Integer(string="Uvt Amount Add")
    is_superior_uvt = fields.Boolean(string="Is Superior UVT", default=False)
    active = fields.Boolean(default=True)
