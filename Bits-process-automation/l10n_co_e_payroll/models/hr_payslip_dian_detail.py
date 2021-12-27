from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _


class HrPayslipDianDetail(models.Model):
    _name = 'hr.payslip.dian.detail'

    request_date = fields.Datetime(
        string='Request Date',
    )
    code = fields.Char(
        string='Code',
        size=2
    )
    description = fields.Char(
        string='Description',
    )
    line_ids = fields.One2many(
        comodel_name='hr.payslip.dian.detail.line',
        inverse_name='detail_id',
        string='Line Details',
    )
    payslip_id = fields.Many2one(
        comodel_name='hr.payslip',
        string='Payslip',
    )
    # MASSIVE PAYSLIP FIELDS
    payslip_run_id = fields.Many2one(
        comodel_name='hr.payslip.run',
        string='Payslip Run',
    )
    general_status = fields.Char(
        string='General Status',
    )
    compute_status = fields.Boolean(
        string='Compute Status',
        compute='_get_general_status',
    )

    def _get_general_status(self):
        for record in self:
            if record.line_ids:
                last_line = False
                for line in record.line_ids:
                    if not last_line:
                        last_line = line
                    elif line.create_date > last_line.create_date:
                        last_line = line
                record.general_status = last_line.status
            else:
                record.general_status = _('Without Information')
            record.compute_status = True


class HrPayslipDianDetailLine(models.Model):
    _name = 'hr.payslip.dian.detail.line'

    number = fields.Char(
        string='number',
    )
    status = fields.Char(
        string='status',
    )
    app_response = fields.Binary(
        string='appResponse',
    )
    xml_signed = fields.Binary(
        string='xmlSigned',
    )
    detail_id = fields.Many2one(
        comodel_name='hr.payslip.dian.detail',
        string='Detail'
    )
    payslip_pdf = fields.Binary(
        string='PDF',
    )


class HrPayslipDianResult(models.Model):
    _name = 'hr.payslip.dian.result'

    request_date = fields.Datetime(
        string='Request Date',
    )
    code = fields.Char(
        string='Code',
        size=2
    )
    description = fields.Char(
        string='Description',
    )
    type = fields.Char(
        string='Type',
    )
    qty = fields.Char(
        string='Qty'
    )
    line_ids = fields.One2many(
        comodel_name='hr.payslip.dian.result.line',
        inverse_name='result_id',
        string='Line Results',
    )
    payslip_id = fields.Many2one(
        comodel_name='hr.payslip',
        string='Payslip',
    )
    payslip_run_id = fields.Many2one(
        comodel_name='hr.payslip.run',
        string='Payslip Run',
    )


class HrPayslipDianResultLine(models.Model):
    _name = 'hr.payslip.dian.result.line'

    number = fields.Char(
        string='Number',
    )
    position = fields.Char(
        string='Position',
    )
    cune = fields.Char(
        string='Cune',
    )
    result = fields.Char(
        string='Result',
    )
    result_id = fields.Many2one(
        comodel_name='hr.payslip.dian.result',
        string='Result'
    )


class HrPayslipDianTotal(models.Model):
    _name = 'hr.payslip.dian.total'

    request_date = fields.Datetime(
        string='Request Date',
    )
    code = fields.Char(
        string='Code',
        size=2
    )
    description = fields.Char(
        string='Description',
    )
    line_ids = fields.One2many(
        comodel_name='hr.payslip.dian.total.line',
        inverse_name='total_id',
        string='Line Totals',
    )
    payslip_id = fields.Many2one(
        comodel_name='hr.payslip',
        string='Payslip',
    )
    payslip_run_id = fields.Many2one(
        comodel_name='hr.payslip.run',
        string='Payslip Run',
    )


class HrPayslipDianTotalLine(models.Model):
    _name = 'hr.payslip.dian.total.line'

    receipts_payslip_status = fields.Char(
        string='ReceiptsPayslipStatus',
    )
    status_payslip = fields.Char(
        string='StatusNomina',
    )
    pasylip_qty = fields.Char(
        string='PasylipQty',
    )
    total_id = fields.Many2one(
        comodel_name='hr.payslip.dian.total',
        string='Total'
    )