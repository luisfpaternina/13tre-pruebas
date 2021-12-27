from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    days_per_period = fields.Float(
        digits=(32, 2), string="Days per period", default=15)

    minimum_days_enjoyed = fields.Float(
        digits=(32, 2), string="Minimum days enjoyed", default=6)

    maximum_days_compensated = fields.Float(
        digits=(32, 2), string="Minimin days compensated", default=5)

    after_x_lapse = fields.Float(
        digits=(32, 2), string="After X lapse", default=5
    )

    additional_days = fields.Float(
        digits=(32, 2), string="Additional day of vacation", default=1
    )
