from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    colombian_exterior = fields.Boolean(
        'Colombian in the Exterior',
        default=False
    )
