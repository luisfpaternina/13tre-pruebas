# Part of Bits. See LICENSE file for full copyright and licensing details.
import logging
from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.tools import float_round
from odoo.tools.misc import format_date
from datetime import datetime
from calendar import monthrange
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class HrPayrollNews(models.Model):
    _name = 'hr.payroll.news'
    _description = 'bits_hr_payroll_news.bits_payroll_news'
    _inherit = ['portal.mixin',
                'mail.thread.cc',
                'mail.activity.mixin',
                'rating.mixin']

    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean('It is active', default=True, tracking=True)
    description = fields.Text(
        string='This is field for description',
        tracking=True)

    salary_rule_code = fields.Char(required=True)

# Fields for replicate new
    replicate_new = fields.Boolean(
        string='Replicate New',
        default=False,
    )

    check_create_replication = fields.Boolean()

    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Important'),
    ], default='0', index=True)

    color = fields.Integer(string='Color Index')
    date_deadline = fields.Date(
        string='Deadline',
        copy=False,
        invisible=1, tracking=True)
    date_start = fields.Date(
        string='Initial date',
        required=True, tracking=True,
        default=datetime.now().strftime('%Y-%m-01'))
    date_end = fields.Date(
        string='End date',
        required=True, tracking=True,
        default=str(datetime.now() + relativedelta(
            months=+1, day=1, days=-1))[:10])
    date_deadline_formatted = fields.Char(
        compute='_compute_date_deadline_formatted')
    payroll_structure_id = fields.Many2one(
        'hr.payroll.structure',
        string='Payroll Structure', tracking=True,
        domain="[('type_id', '!=', False), ('type_id.is_novelty', '=', True)]",
        required=True)
    payroll_structure_name = fields.Char(
        related='payroll_structure_id.name',
        readonly=True)
    salary_rule_id = fields.Many2one(
        'hr.salary.rule',
        string='Salary rule', track_visibility="onchange",
        domain="[('struct_id', '=', payroll_structure_id)]",
        required=True)
    salary_rule_name = fields.Char(
        related='salary_rule_id.name',
        readonly=True)
    request_date_from = fields.Date(
        string='Request Start Date', tracking=True)
    request_date_to = fields.Date(
        string='Request End Date', tracking=True)

    date_range_apply = fields.Boolean(
        related='payroll_structure_id.date_range_apply',
        default=False,
        invisible=1)

    condition_holiday = fields.Selection(
        related='salary_rule_id.condition_holiday',
        readonly=True)

    l10n_type_rule = fields.Char()

    def _default_stage_id(self):
        return self._stage_find(domain=[('sequence', '=', 1)]).id

    stage_id = fields.Many2one(
        'hr.payroll.news.stage',
        string='Stage',
        ondelete='restrict', tracking=True,
        copy=False,
        group_expand='_read_group_stage_ids',
        default=_default_stage_id)

    is_liquidated = fields.Boolean(
        related='stage_id.is_won',
        string='Liquidated',
        readonly=True,
        related_sudo=False)

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

    kanban_state = fields.Selection([
        ('normal', 'Grey'),
        ('done', 'Green'),
        ('blocked', 'Red')], string='State Kanban',
        copy=False, default='normal', required=True)
    kanban_state_label = fields.Char(
        compute='_compute_kanban_state_label',
        string='Kanban State',
        tracking=True)

    legend_blocked = fields.Char(
        related='stage_id.legend_blocked',
        string='Kanban Blocked Explanation',
        readonly=True,
        related_sudo=False)
    legend_done = fields.Char(
        related='stage_id.legend_done',
        string='Kanban Valid Explanation',
        readonly=True,
        related_sudo=False)
    legend_normal = fields.Char(
        related='stage_id.legend_normal',
        string='Kanban Ongoing Explanation',
        readonly=True,
        related_sudo=False)

    stage_name = fields.Char(related='stage_id.name', readonly=True)

    employee_payroll_news_ids = fields.One2many(
        'hr.employee.payroll.news',
        'payroll_news_id', track_visibility="onchange",
        string='Employee Payroll News',
        help='Employee Payroll News Information')

    label_employees = fields.Char(
        string='Use Employee as',
        default='Employees',
        help="Label used for the employees.")
    employee_count = fields.Integer(
        compute='_compute_employee_count',
        string="Count Employee")

    @api.onchange('payroll_structure_id')
    def _onchange_payroll_structure_id(self):
        self.ensure_one()
        self.salary_rule_id = False
        self.request_date_from = False
        self.request_date_to = False

    @api.onchange('salary_rule_id')
    def _onchange_salary_rule_id(self):
        self.ensure_one()
        if not self.salary_rule_id:
            return {}
        for line in self.employee_payroll_news_ids:
            if self.date_range_apply and not self.\
               _check_dates(self.request_date_from, self.request_date_to):
                line.quantity = line._get_calendar_number_of_days(
                    self.request_date_from,
                    self.request_date_to)['days']
            line.amount = line._get_amount_compute_rule()
            line.total = line.quantity * line.amount

    def _check_dates(self, date_start, date_end):
        self.ensure_one()
        start = date_start or False
        end = date_end or False
        if start and end and date_end >= date_start:
            return False
        return True

    @api.constrains('employee_payroll_news_ids')
    def _check_employee_payroll_news_ids(self):
        for record in self:
            if not record.employee_count > 0:
                raise ValidationError(
                    _('Error! Must add employee to novelty'))
            if record.date_range_apply and not record.employee_count == 1:
                raise ValidationError(
                    _('Error! You must add only one employee.'))

    @api.constrains('date_start', 'date_end')
    def _check_date_end(self):
        for record in self:
            if record._check_dates(self.date_start, self.date_end):
                raise ValidationError(
                    _('Error! The final date for the calculation of the \
                      payroll news cannot be less than the initial date'))

    @api.constrains('request_date_from', 'request_date_to')
    def _check_request_date_to(self):
        for record in self:
            if record.date_range_apply and record.\
               _check_dates(self.request_date_from, self.request_date_to):
                raise ValidationError(
                    _('Error! The start date for the range of days in \
                      absences must be greater than the end date'))

    @api.onchange('request_date_from', 'request_date_to')
    def _onchange_request_date(self):
        self.ensure_one()
        if self._check_dates(self.request_date_from, self.request_date_to):
            return {}

        for line in self.employee_payroll_news_ids:
            line.quantity = line._get_calendar_number_of_days(
                self.request_date_from,
                self.request_date_to)['days']

    @api.depends('date_deadline')
    def _compute_date_deadline_formatted(self):
        for hr_payroll_news in self:
            hr_payroll_news.date_deadline_formatted = format_date(
                self.env,
                hr_payroll_news.date_deadline) if \
                hr_payroll_news.date_deadline else None

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        logging.getLogger('_onchange_sta1ge_id')

    @api.depends('stage_id', 'kanban_state')
    def _compute_kanban_state_label(self):
        for hr_payroll_news in self:
            if hr_payroll_news.kanban_state == 'normal':
                hr_payroll_news.kanban_state_label = hr_payroll_news.\
                                                     legend_normal
            elif hr_payroll_news.kanban_state == 'blocked':
                hr_payroll_news.kanban_state_label = hr_payroll_news.\
                                                     legend_blocked
            else:
                hr_payroll_news.kanban_state_label = hr_payroll_news.\
                                                     legend_done

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env['hr.payroll.news.stage'].search([])
        return stage_ids

    def _stage_find(self, domain=None, order='sequence'):
        search_domain = []
        res = self.env['hr.payroll.news.stage'].search(
            domain, order=order, limit=1)
        return res

    def _compute_employee_count(self):
        if not self.ids:
            return None

        employee_data = self.env['hr.employee.payroll.news'].read_group(
            [('payroll_news_id', 'in', self.ids)],
            ['payroll_news_id'],
            ['payroll_news_id'])
        result = dict(
            (data['payroll_news_id'][0],
                data['payroll_news_id_count']) for data in employee_data)
        for hr_payroll_news in self:
            hr_payroll_news.employee_count = result.get(hr_payroll_news.id, 0)

    def replicate_new_amount(self, vals, init_date, final_date):
        date_iteration = init_date
        date_iteration = date_iteration + relativedelta(months=+1)
        date_iteration = date_iteration.replace(day=1)
        final_date = datetime.strptime(final_date, '%Y-%m-%d')\
            if type(final_date) == str else final_date
        final_date = final_date.date()\
            if type(final_date) == datetime else final_date
        date_iteration = date_iteration.date()\
            if type(date_iteration) == datetime else date_iteration

        while date_iteration.replace(day=1) < final_date.replace(day=1):
            vals['message_follower_ids'] = []
            end_date = self.last_day_of_month(date_iteration)
            vals['date_start'] = date_iteration
            vals['date_end'] = end_date

            if vals.get('request_date_from', False):
                vals['request_date_from'] = date_iteration
                vals['request_date_to'] = end_date

            result = self.create(vals)
            date_iteration = date_iteration + relativedelta(months=+1)

        vals['message_follower_ids'] = []
        vals['date_start'] = date_iteration
        vals['date_end'] = final_date

        if vals.get('request_date_from', False):
            vals['request_date_from'] = date_iteration
            vals['request_date_to'] = final_date

        result = self.create(vals)

    def last_day_of_month(self, dateValue):
        return dateValue.replace(day=monthrange(
            dateValue.year, dateValue.month)[1])

    def request_date(self, vals):
        vals.ensure_one()
        if vals._check_dates(vals.request_date_from, vals.request_date_to):
            return {}

        for line in vals.employee_payroll_news_ids:
            line.quantity = line._get_calendar_number_of_days(
                vals.request_date_from,
                vals.request_date_to)['days']

    @api.model
    def create(self, vals):
        # Calculo de amount novedades, carga masiva
        if not vals.get('employee_payroll_news_ids'):
            raise ValidationError(
                _(
                    """
                        Error! Must add employee to novelty
                    """
                )
            )
        if vals.get('salary_rule_code'):
            rule = self.env['hr.salary.rule'].search(
                [
                    ('code', '=', vals.get('salary_rule_code')),
                    ('struct_id.type_id.is_novelty', "=", True)
                ],
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

            for item in vals['employee_payroll_news_ids']:
                # Novedades si valor definido o igual a 0
                if item[2]['amount']:
                    continue
                # Novedades si valor definido
                item[2]['amount'] = self._calculate_quantity_of_news(
                    item, rule)
        else:
            result = self.env['hr.salary.rule'].browse(
                vals.get('salary_rule_id'))
            vals['salary_rule_code'] = result.code

        # Validate duplicate novelty
        if not vals.get('check_create_replication', False) \
                and vals.get('replicate_new', False):
            init_date_time = vals.get('date_start')
            final_date = vals.get('date_end')
            if type(init_date_time) is str:
                init_date_time = datetime.strptime(init_date_time, '%Y-%m-%d')
                final_date = datetime.strptime(final_date, '%Y-%m-%d')

            if vals.get('request_date_from', False):
                vals['request_date_to'] = self.last_day_of_month(
                    init_date_time)
                vals['request_date_from'] = vals['date_start']
            vals['date_end'] = self.last_day_of_month(init_date_time)

        result = super(HrPayrollNews, self).create(vals)

        if vals.get('replicate_new', False):
            self.request_date(result)

        for line in result.employee_payroll_news_ids:
            msg = line._message_post_create_line({
                'employee_id': line.employee_id.id,
                'quantity': line.quantity,
                'amount': line.amount,
                'total': line.quantity*line.amount,
            })
            result.message_post(body=msg)

        # Duplicate new method
        if not vals.get('check_create_replication', False) \
                and vals.get('replicate_new', False):
            vals['check_create_replication'] = True
            self.replicate_new_amount(vals, init_date_time, final_date)

        return result

    def _calculate_quantity_of_news(self, item, rule):
        quantity = item[2]['quantity']

        employee = self.env['hr.employee'].search(
            [
                ('identification_id', '=', item[2]['identification_id'])
            ],
            limit=1
        )

        if not employee:
            raise ValidationError(
                _('Error! the employee does not exist')
            )
        if not employee.contract_id or employee.contract_id.state != 'open':
            raise ValidationError(
                _('Error! the employee contract does not configured')
            )

        contract = employee.contract_id

        localdict = {
            **self._get_base_local_dict(),
            **{
                'employee': employee,
                'contract': contract
            }
        }

        localdict.update({
            'result': None,
            'result_qty': quantity,
            'result_rate': 100
        })
        if rule._satisfy_condition(localdict):
            amount, qty, rate = rule._compute_rule(localdict)
            tot_rule = amount * qty * rate / 100.0
            return tot_rule

    def _get_base_local_dict(self):
        return {
            'float_round': float_round
        }

    def write(self, vals):
        if 'stage_id' in vals:
            if 'kanban_state' not in vals:
                vals['kanban_state'] = 'normal'

        result = super(HrPayrollNews, self).write(vals)
        return result

    def _track_subtype(self, init_values):
        return super(HrPayrollNews, self)._track_subtype(init_values)

    sum_total = fields.Integer(
        compute='_compute_total_employee_payroll_news',
        string="Total sum lines"
    )

    @api.depends('employee_payroll_news_ids')
    def _compute_total_employee_payroll_news(self):
        for record in self:
            total = sum(record.mapped('employee_payroll_news_ids.total'))
            record.sum_total = total

    def action_add_employees(self):
        self.ensure_one()
        compose_form = self.env.ref(
            'bits_hr_payroll_news.payroll_news_wizard_form',
            raise_if_not_found=False)
        ctx = dict(
            default_parent_model='hr.employee.payroll.news',
            default_model='hr.payroll.news',
            default_payroll_structure_id=self.payroll_structure_id.id,
            default_salary_rule_id=self.salary_rule_id.id,
            parent_ids=self.ids,
        )
        return {
            'name': _('Add Employees'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.payroll.news.wizard',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }
