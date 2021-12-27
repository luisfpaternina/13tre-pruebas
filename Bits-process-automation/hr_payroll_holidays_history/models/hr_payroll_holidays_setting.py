from odoo import models, fields, api, _
from ast import literal_eval


class HrPayrollHolidaysSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    days_per_period = fields.Float(
        string="Days per period",
        related="company_id.days_per_period",
        readonly=False
    )

    minimum_days_enjoyed = fields.Float(
        string="Minimum days enjoyed",
        related="company_id.minimum_days_enjoyed",
        readonly=False
    )

    maximum_days_compensated = fields.Float(
        string="Maximum days compesated",
        related="company_id.maximum_days_compensated",
        readonly=False
    )

    after_x_lapse = fields.Float(
        string="After X lapse",
        related="company_id.after_x_lapse",
        readonly=False
    )

    additional_days = fields.Float(
        string="Additional days",
        related='company_id.additional_days',
        readonly=False
    )

    holiday_structure_ids = fields.Many2many(
        'hr.payroll.structure',
        'holiday_structure_ids_table',
        string='Holidays Structures'
    )

    def set_values(self):
        res = super(HrPayrollHolidaysSetting, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'many2many.holiday_structure_ids', self.holiday_structure_ids.ids)
        return res

    @api.model
    def get_values(self):
        res = super(HrPayrollHolidaysSetting, self).get_values()
        with_user = self.env['ir.config_parameter'].sudo()
        holiday_structure_ids = with_user.get_param(
            'many2many.holiday_structure_ids')
        res.update(
            holiday_structure_ids=[(6, 0, literal_eval(holiday_structure_ids))]
            if holiday_structure_ids else False
        )
        return res
