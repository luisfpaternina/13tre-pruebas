from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class HrPayslipEmployeesInherit(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    def compute_sheet(self):
        payslip = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))
        employees_name = []
        for employee in self.employee_ids:
            if employee.contributor_type.code in ['20','40','59']:
                employees_name.append(employee.name)

        if employees_name:
            raise UserError(
                _('No se puede calcular una nómina para %s con este tipo de contribuyente' % (employees_name))
            )

        payment_date = payslip.payment_date
        payment_method_id = payslip.payment_method_id.id
        payment_way_id = payslip.payment_way_id.id
        records = self.with_context(
                                    default_payment_date = payment_date,
                                    default_payment_method_id = payment_method_id,
                                    default_payment_way_id = payment_way_id)
        res = super(HrPayslipEmployeesInherit, records).compute_sheet()
        return res
