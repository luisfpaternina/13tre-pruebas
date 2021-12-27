# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from calendar import monthrange
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class HrPayrollNewsBatch(models.Model):
    _name = 'hr.payroll.news.batch'
    _description = 'bits_hr_payroll_news_batch.bits_hr_payroll_news_batch'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    description = fields.Text()

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True,
        readonly=True,
        default=lambda self: self.env.company.currency_id.id
    )

    method_number = fields.Integer(
        string='Number of Depreciations',
        default=1,
        help="The number of depreciations needed to depreciate your asset"
    )
    method_period = fields.Selection(
        [('1', 'Months')],
        string='Number of Months in a Period',
        default='1',
        help="The amount of time between two depreciations"
    )

    make_depreciation = fields.Boolean(
        'Is depreciable',
        required=True,
        default=True
    )

    fixed_value = fields.Monetary(string='Fixed Value', store=True)
    original_value = fields.Monetary(string="Original Value", store=True)
    value_residual = fields.Monetary(
        string='Book Value',
        readonly=True,
        compute='_compute_book_value')

    paid_value = fields.Monetary(
        digits=0,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help="It is the amount you plan to have that you cannot depreciate.",
        compute='_compute_book_value')

    # Dates
    first_depreciation_date = fields.Date(
        string='First Depreciation Date',
        required=True,
        default=str(datetime.now() + relativedelta(
            months=+1, day=1, days=-1))[:10],
        help='',
    )
    date_end = fields.Date('Date end', compute='_compute_date_end')
    acquisition_date = fields.Date(default=datetime.now())
    disposal_date = fields.Date()

    payroll_structure_id = fields.Many2one(
        'hr.payroll.structure',
        string='Payroll Structure', tracking=True,
        domain="[('type_id', '!=', False), ('type_id.is_novelty', '=', True)]",
        required=True)
    salary_rule_id = fields.Many2one(
        'hr.salary.rule',
        string='Salary rule', track_visibility="onchange",
        domain="[('struct_id', '=', payroll_structure_id)]",
        required=True)
    salary_rule_code = fields.Char('Salary rule code')
    salary_rule_code_value = fields.Char(
        'rule code',
        related='salary_rule_id.code'
    )

    user_id = fields.Many2one(
        'res.users',
        string='Assigned to',
        default=lambda self: self.env.uid,
        index=True, tracking=True, required=True)

    email_from = fields.Char(
        related='user_id.email',
        string='User Email',
        readonly=True,
        related_sudo=False)

    employee_id = fields.Many2one(
        'hr.employee',
        required=True,
        string="Employee",
        help='Select corresponding Employee')
    number_identification = fields.Char(
        'Number Identification',
        related='employee_id.identification_id'
    )
    identification_id = fields.Char(
        'Identification number'
    )

    children_ids = fields.One2many(
        'hr.payroll.news',
        'batch_id',
        string="Payroll news",
        help="")

    state = fields.Selection(
        [('draft', 'Draft'),
         ('open', 'Running'),
         ('paused', 'On Hold'),
         ('close', 'Closed')],
        'Status', copy=False, tracking=True, default='draft')

    @api.model
    def create(self, vals):
        if vals.get('identification_id') and not vals.get('employee_id'):
            employee = self.env['hr.employee'].search(
                [('identification_id', '=', vals.get('identification_id'))],
                limit=1).id
            vals['employee_id'] = employee
            if not employee > 0:
                raise ValidationError(
                    _('Error! There is no employee with \
                      the identification number %s.')
                    % vals.get('identification_id'))
        if vals.get('salary_rule_code') and not vals.get('salary_rule_id'):
            rule = self.env['hr.salary.rule'].search([
                ('code', '=', vals.get('salary_rule_code')),
                ('struct_id.type_id.is_novelty', "=", True)],
                limit=1
            )
            if not rule or not rule.struct_id:
                raise ValidationError(
                    _(
                        """
                            Error! the rule with the entered code does not
                            exist or the wage rule does not have a structure
                        """
                    )
                )
            vals['salary_rule_id'] = rule.id
            vals['payroll_structure_id'] = rule.struct_id.id

        return super(HrPayrollNewsBatch, self).create(vals)

    def _compute_date_end(self):
        for batch in self:
            batch.date_end = None

            if batch.make_depreciation:
                batch.date_end = batch.first_depreciation_date\
                    + relativedelta(months=+batch.method_number)

    def _compute_book_value(self):
        stage_id = self._stage_find(domain=[('is_won', '=', True)])
        for record in self:
            _ids = record.children_ids\
                .filtered(lambda x: x.stage_id.id == stage_id)\
                .sorted(key=lambda l: l.date_start)
            total = sum(_ids.mapped('sum_total'))
            record.paid_value = total
            record.value_residual = record.original_value - record.paid_value

    def create_payroll_news(self, index, total):
        depreciation_date = self.first_depreciation_date \
            + relativedelta(months=+int(index))
        first_depreciation_date = depreciation_date + relativedelta(day=1)
        amount = (self.fixed_value if self.fixed_value
                  else self.original_value / total)

        stage_id = self._stage_find(domain=[('sequence', '=', 100)])

        liquidated_date = datetime.now().date() + relativedelta(months=-1)
        if (depreciation_date.month <= liquidated_date.month
                or depreciation_date.year < liquidated_date.year):
            stage_id = self._stage_find(domain=[('is_won', '=', True)])

        if (depreciation_date.month == datetime.now().month
                and depreciation_date.year == datetime.now().year):
            stage_id = self._stage_find(domain=[('is_approved', '=', True)])

        line = {
            "quantity": 1,
            "payroll_news_id": False,
            "employee_id": self.employee_id.id,
            "amount": amount,
        }

        _ref = self.name
        if self.make_depreciation:
            _ref += ' (%s/%s)' % (index+1, self.method_number)
        else:
            _ref += ' (%s)' % (index+1)

        ctx = dict(
            name=_ref,
            date_start=first_depreciation_date,
            date_end=depreciation_date,
            user_id=self.user_id.id,
            payroll_structure_id=self.payroll_structure_id.id,
            salary_rule_id=self.salary_rule_id.id,
            batch_id=self.id,
            stage_id=stage_id,
            employee_payroll_news_ids=[[
                0,
                0,
                line
            ]])
        return ctx

    def _stage_find(self, domain=[('sequence', '=', 1)], order='sequence'):
        res = self.env['hr.payroll.news.stage'].search(
            domain, order=order, limit=1).id
        return res

    def _recompute_board(self):
        newline_vals_list = []
        stage_id = self._stage_find(domain=[('is_won', '=', True)])
        amount_change_ids = self.children_ids\
            .sorted(key=lambda l: l.date_start)
        amount_to_depreciate = sum([m.sum_total for m in amount_change_ids])
        _ids = self.children_ids\
            .filtered(lambda x: x.stage_id.id == stage_id)\
            .sorted(key=lambda l: l.date_start)
        already_amount = sum([m.sum_total for m in _ids])
        _sequence = 0

        # fixed number
        _f_number = self._calculate_amount_of_news(
            self.first_depreciation_date)
        _number = (_f_number
                   if not self.make_depreciation and _f_number > 0
                   else self.method_number)

        for sequence in range(_sequence, _number):
            newline_vals = self.create_payroll_news(sequence, _number)
            newline_vals_list.append(newline_vals)

        return newline_vals_list

    def compute_payroll_news_board(self):
        self.ensure_one()

        commands = [(2, line_id.id, False) for line_id in self.children_ids]
        newline_vals_list = self._recompute_board()
        new_records = self.env['hr.payroll.news'].create(newline_vals_list)
        for record in new_records:
            commands.append((4, record.id))
        return self.write({'children_ids': commands})

    def validate(self):
        stage_ids = self.env['hr.payroll.news.stage'].search(
            ['|', ('is_won', '=', True), ('is_approved', '=', True)]).ids
        self.env['hr.payroll.news'].search([
            ('batch_id', '=', self.id),
            ('stage_id', 'not in', stage_ids)
        ]).write({
            'stage_id': self._stage_find()
        })

        self.write({
            'state': 'open',
        })

    def inactive_childrens(self):
        stage_ids = stage_ids = self.env['hr.payroll.news.stage'].search(
            [('is_won', '=', True)]).ids
        _ids = self.children_ids\
            .filtered(lambda x: x.stage_id.id in stage_ids)
        self.env['hr.payroll.news'].search([
            ('batch_id', '=', self.id),
            ('stage_id', 'not in', stage_ids)
        ]).write({
            'stage_id': self._stage_find(domain=[('sequence', '=', 100)])
        })

    def action_set_to_close(self):
        for batch in self:
            batch.inactive_childrens()
            batch.write({'state': 'close'})

    def set_to_draft(self):
        stage_ids = stage_ids = self.env['hr.payroll.news.stage'].search(
            ['|', ('is_won', '=', True), ('is_approved', '=', True)]).ids
        _ids = self.children_ids\
            .filtered(lambda x: x.stage_id.id in stage_ids)

        if _ids:
            raise ValidationError(
                _("Error! You cannot change the status of the record, you \
                  already have payroll news in liquidated or approved status"))

        self.env['hr.payroll.news'].search([
            ('batch_id', '=', self.id),
            ('stage_id', 'not in', stage_ids)
        ]).write({
            'stage_id': self._stage_find(domain=[('sequence', '=', 100)])
        })
        self.write({'state': 'draft'})

    def _generate_fixed_novelties(self):
        novelties_batch = self.env['hr.payroll.news.batch'].search([
            ('make_depreciation', '=', False),
            ('state', '=', 'open')
        ])

        c_date = datetime.now()
        stage_id = self._stage_find(domain=[('is_approved', '=', True)])
        for novelty_b in novelties_batch:
            if c_date.month == novelty_b.first_depreciation_date.month \
                    and c_date.year == novelty_b.first_depreciation_date.year:
                continue

            novelty_created = novelty_b.children_ids.filtered(
                lambda x: x.date_start.month == c_date.month
                and x.date_start.year == c_date.year)

            if not novelty_created:
                sequence = (c_date.year -
                            novelty_b.first_depreciation_date.year) * 12\
                    + c_date.month - novelty_b.first_depreciation_date.month

                new_novelty = novelty_b.create_payroll_news(sequence, 0)
                new_novelty['stage_id'] = stage_id
                self.env['hr.payroll.news'].create(new_novelty)

        self.update_state_novelties(c_date, stage_id)

    def update_state_novelties(self, c_date, stage_id):

        last_day_month = monthrange(c_date.year, c_date.month)[1]
        date_from = c_date.replace(day=1)
        date_to = c_date.replace(day=last_day_month)

        novelties_created = self.env['hr.payroll.news'].search([
            ('batch_id', '!=', None),
            ('batch_id.make_depreciation', '=', True),
            ('batch_id.state', '=', 'open'),
            ('date_start', '>=', date_from),
            ('date_end', '<=', date_to),
            ('stage_id.sequence', '=', 1)
        ])

        novelties_created.write({
            'stage_id': stage_id
        })

    def _calculate_amount_of_news(self, init_date):
        _f_number = 1
        _c_date = datetime.now()
        diff_date = relativedelta(_c_date, init_date)

        _f_number += 12 * diff_date.years
        _f_number += diff_date.months

        if init_date.day > _c_date.day:
            _f_number += 1

        return _f_number

    def _compute_all_payroll_news_board(self):
        for p_batch in self:
            if p_batch.state != 'draft':
                continue

            p_batch.compute_payroll_news_board()

    def _approved_all_batch(self):
        for batch in self:
            if batch.state != 'draft':
                continue

            batch.validate()

    @api.onchange('employee_id', 'salary_rule_id')
    def _onchange_name(self):
        self.name = '%s - %s' % (
            self.employee_id.name if self.employee_id else '',
            self.salary_rule_id.name if self.salary_rule_id else '')

    @api.onchange('make_depreciation')
    def _change_depreciation(self):
        if not self.make_depreciation:
            self.method_number = 1
            self.original_value = 0
        else:
            self.fixed_value = 0

    def write(self, vals):
        if 'state' in vals and vals['state'] == 'close':
            self.inactive_childrens()

        return super(HrPayrollNewsBatch, self).write(vals)


class HrPayrollNews(models.Model):
    _inherit = 'hr.payroll.news'

    batch_id = fields.Many2one(
        'hr.payroll.news.batch',
        help=""
    )

    sum_total = fields.Integer(
        compute='_compute_total_employee_payroll_news',
        string="Total sum lines"
    )

    @api.depends('employee_payroll_news_ids')
    def _compute_total_employee_payroll_news(self):
        for record in self:
            total = sum(record.mapped('employee_payroll_news_ids.total'))
            record.sum_total = total
