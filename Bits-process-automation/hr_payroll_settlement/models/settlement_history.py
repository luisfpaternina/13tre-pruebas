# -*- coding: utf-8 -*-

from ast import literal_eval
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class SettlementHistory(models.Model):
    _name = 'settlement.history'

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('done', 'Done'),
            ('cancel', 'Cancelled')
        ],
        string='Status',
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
        default='draft'
    )
    contract_id = fields.Many2one('hr.contract', required=True)
    employee_id = fields.Many2one('hr.employee', required=True)
    reason_for_termination = fields.Many2one(
        'reasons.for.termination',
        string="Reason for termination",
        required=True
    )
    type_contract = fields.Selection([
        ('1', 'Término fijo'),
        ('2', 'Término indefinido'),
        ('3', 'Obra o labor'),
        ('4', 'Aprendizaje'),
        ('5', 'Práctica o pasantía')],
        default="1",
        related='contract_id.type_contract',
        required=True
    )
    date_end = fields.Date(
        required=True,
        default=datetime.now().strftime('%Y-%m-%d')
    )

    period = fields.Selection([
        ('monthly', 'Monthly Fixed Wage'), ('hourly', 'Hourly Wage')],
        related='contract_id.wage_type'
    )
    proccess = fields.Integer()
    date_payment = fields.Date(required=True)
    compensation = fields.Boolean(required=True)
    confidential = fields.Boolean()
    news_deadline = fields.Date()
    state_settlement = fields.Selection(
        [
            ('active', 'Active'),
            ('retired', 'Retired')
        ],
        default="active",
        required=True
    )
    comments = fields.Text()
    days_unpaid = fields.Float()
    pending_vacation_days = fields.Float(
        string="Pending vacation days",
        default=0,
        compute="_get_total_pending_vacation_days"
    )

    payslip_id = fields.Many2one(
        'hr.payslip',
        string='Payslip',
        # required=True,
        ondelete='cascade',
        index=True)

    # Duracion del contrato Total de meses
    contract_duration = fields.Float()

    # Duracion del contrato Total de meses
    running_time = fields.Float()

    # Cuando es contrato a termino fijo debe der llenado
    missing_time = fields.Float(default=0)

    # Dias trabajados
    work_days = fields.Integer(compute="_compute_work_days")

    @api.onchange('employee_id')
    def _onchange_employee(self):
        if not self.employee_id:
            return

        employee_id = self.employee_id
        date_from = fields.Date.to_string(date.today().replace(day=1))
        date_to = fields.Date.to_string((
            datetime.now() + relativedelta(months=+1, day=1, days=-1)).date())

        self.days_unpaid = self.get_total_unpaid_news()
        # Add a default contract_id if not already defined
        contracts = employee_id._get_contracts(date_from, date_to)
        if not contracts:
            self.contract_id = False
            self.date_end = False
            return
        self.contract_id = contracts[0]

    @api.onchange('contract_id')
    def _onchange_contract(self):
        date_end = False
        if self.contract_id.date_end:
            date_end = self.contract_id.date_end
            self.type_contract = '1'
        self.period = self.contract_id.wage_type
        self.set_contract_duration()

    @api.onchange('date_end')
    def _onchange_date_end(self):
        if self.date_end:
            self.set_contract_duration()

    @api.constrains('date_end')
    def _check_validate_date_end(self):
        if (
            self.contract_id.date_end
            and
            self.type_contract == 'fixed'
        ):
            if self.date_end > self.contract_id.date_end:
                raise ValidationError(
                    'The settlement date cannot be more recent than the' +
                    'expiration date of the contract'
                )

    def days_360(self, date1, date2):
        if not date1 or not date2:
            return 0
        start_day = date1.day
        end_day = date2.day

        if start_day == 31:
            start_day = 30

        if end_day == 31:
            end_day = 30

        days_diff = (date2.year - date1.year) * 360
        days_diff += (date2.month - date1.month) * 30
        days_diff += (end_day - start_day) + 1

        return days_diff

    @api.depends('date_end', 'contract_id')
    def _compute_work_days(self):
        for record in self:
            record.work_days = record.days_360(
                record.contract_id.date_start,
                record.date_end)

    def set_contract_duration(self):
        self.running_time = self.days_360(
            self.contract_id.date_start, self.date_end) / 30

        self.contract_duration = self.days_360(
            self.contract_id.date_start, self.contract_id.date_end) / 30

        self.missing_time = self.contract_duration - self.running_time\
            if (self.contract_duration - self.running_time) > 0 else 0

    # def update_date_contract(self):
    #     if self.type_contract == 'non-fixed':
    #         self.env['hr.contract'].search(
    #             [
    #                 ('id', '=', self.contract_id.id)
    #             ]
    #         ).write({
    #             'date_end': self.date_end
    #         })

    def action_cancel(self):
        self.payslip_id.action_payslip_cancel()
        self.write({
            'state': 'cancel',
        })

    def action_draft(self):
        self.write({
            'state': 'draft',
        })

    def calculate_payroll_news_batch(self):
        batch_ids = self.env['hr.payroll.news.batch'].search([
            ('employee_id', '=', self.employee_id.id),
            ('state', '=', 'open')
        ])
        stage_ids = self.env['hr.payroll.news.stage'].search(
            ['|', ('sequence', '=', 1), ('is_approved', '=', True)]).ids

        cancel_id = self.env['hr.payroll.news.stage'].search(
            [('sequence', '=', 100)]).id

        approve_id = self.env['hr.payroll.news.stage'].search(
            [('is_approved', '=', True)]).id
        for batch_id in batch_ids:
            line_ids = batch_id.children_ids.filtered(
                lambda line: line.stage_id.id in stage_ids)

            if len(line_ids) > 0 and line_ids[0]:
                total = sum(line_ids.mapped('sum_total'))
                line_ids.write({
                    'stage_id': cancel_id
                })

                line_ids[0].write({
                    'stage_id': approve_id
                })

                line_ids[0].employee_payroll_news_ids.write({
                    'amount': total
                })

    def create_payslip(self):
        work_entry_type = self.env.ref(
            'hr_work_entry.work_entry_type_attendance')

        date_from = self.date_end.replace(day=1)
        date_from = date_from if self.contract_id.date_start < date_from\
            else self.contract_id.date_start
        date_to = self.date_end

        number_of_days = self._get_current_payslip(date_from, date_to)

        work_days = ((date_to - date_from).days) + 1
        work_days = 30 if work_days >= 30 else work_days
        work_days -= number_of_days

        return self.env['hr.payslip'].create({
            'name': _('Settlement - %s') % (self.employee_id.name),
            'date_from': date_from,
            'date_to': date_to,
            'employee_id': self.employee_id.id,
            'contract_id': self.contract_id.id,
            'struct_id': self.reason_for_termination.salary_structure.id,
            'worked_days_line_ids': [(0, 0, {
                'work_entry_type_id': work_entry_type.id,
                # Calcular el total de dias trabajados
                'number_of_days': work_days,
                'amount': self.contract_id.wage
            })],
            'payment_date': self.date_payment,
        })

    def validate(self):
        # Unificar las novedades batch en una sola para ser
        # cobranda en el mes de la liquidacion
        # self.update_date_contract()
        self.calculate_payroll_news_batch()
        # Crear Nomina con los datos de la liquidacion
        payslip_id = self.create_payslip()
        self.write({
            'payslip_id': payslip_id.id,
            'state': 'done',
        })
        #raise ValidationError('This is the test')

    # Cambiar meses a float
    def _get_total_month(self, start, end):
        return 0 if (not start or not end) \
            else (end.year - start.year) * 12 + ((end.month - start.month)+1)

    def _get_current_payslip(self, date_from, date_to):
        payslip = self.env['hr.payslip'].search([
            ('employee_id', '=', self.employee_id.id),
            ('date_from', '<=', date_from),
            ('date_to', '>=', date_to),
            '|',
            ('state', '=', 'verify'),
            ('state', '=', 'done')
        ], limit=1)

        if not payslip:
            return 0

        number_of_days = sum(
            [entry.number_of_days for entry in payslip.worked_days_line_ids])
        return number_of_days

    def _get_payroll_news_ids(self, rules, from_date=None, to_date=None):
        domain = [
            ('employee_id', '=', self.employee_id.id),
            ('payroll_news_id.salary_rule_id', 'in', rules)
        ]

        if from_date:
            domain += [('payroll_news_id.date_start', '>=', from_date)]
        if to_date:
            domain += [('payroll_news_id.date_end', '<=', to_date)]

        domain += [
            '|', ('payroll_news_id.stage_id.is_approved', '=', True),
            ('payroll_news_id.stage_id.is_won', '=', True)
        ]

        return self.env['hr.employee.payroll.news'].search(domain)

    def get_total_unpaid_news(self, from_date=None, to_date=None):
        rule_unpaid_ids = self.env['ir.config_parameter'].sudo()\
            .get_param('many2many.rule_unpaid_ids')

        if not rule_unpaid_ids:
            return 0

        _ids = literal_eval(rule_unpaid_ids)
        lines = self._get_payroll_news_ids(_ids, from_date, to_date)
        days_unpaid = sum([line.quantity for line in lines])
        return days_unpaid

    @api.depends('work_days')
    def _get_total_pending_vacation_days(self):
        for record in self:
            self.pending_vacation_days = self.get_total_enjoyed_holidays(
                record)

    def get_total_enjoyed_holidays(self, record):
        # TODO traer esta informacion desde el libro de vacaciones
        holiday_lapses = self.env["hr.payroll.holiday.lapse"].search([
            ("employee_id", "=", self.employee_id.id),
            ("state", "!=", "3")
        ])
        days_taken = 0
        for holiday_lapses in holiday_lapses:
            days_taken += holiday_lapses.days_taken

        quantity_pending_vacation_days = (record.work_days / 360 * 15 if
                                          record.work_days else 0) - days_taken
        return quantity_pending_vacation_days
