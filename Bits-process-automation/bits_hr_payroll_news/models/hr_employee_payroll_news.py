# Part of Bits. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_round, date_utils
from odoo.tools.safe_eval import safe_eval
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
from datetime import datetime, date, timedelta, time
from pytz import timezone, UTC


class HrEmployeePayrollNews(models.Model):

    _name = 'hr.employee.payroll.news'
    _description = 'HR employee payroll news'

    payroll_news_id = fields.Many2one('hr.payroll.news', invisible=1)

    employee_id = fields.Many2one(
        'hr.employee',
        required=True,
        string="Employee",
        help='Select corresponding Employee')

    identification_id = fields.Char(
        related='employee_id.identification_id',
        readonly=False,
        related_sudo=False)
    quantity = fields.Float(string='Units', default=1.0, required=True, digits="Payslip Line Quantity")
    amount = fields.Float(
        string='Quantity',
        required=True,
        digits="Payslip Line Amount")
    total = fields.Float(
        compute='_compute_total',
        string='Total quantity',
        digits='Payslip Line Total',
        required=True)
    stage_name = fields.Char(
        string='Stage by name',
        related='payroll_news_id.stage_name',
        default="")
    structure_name = fields.Char(
        string='Payroll structure',
        related='payroll_news_id.payroll_structure_name',
        default="")
    rule_name = fields.Char(
        string='Salary rule',
        related='payroll_news_id.salary_rule_name',
        default="")

    date_from = fields.Date(
        related='payroll_news_id.request_date_from')
    date_to = fields.Date(
        related='payroll_news_id.request_date_to')

    @api.depends('quantity', 'amount')
    def _compute_total(self):
        for line in self:
            line.total = float(line.quantity) * line.amount

    def _get_amount_compute_rule(self):
        employee = self.employee_id

        if not employee.id or not self.employee_id.contract_id:
            return False

        contract = self.employee_id.contract_id

        localdict = {
            **self._get_base_local_dict(),
            **{
                'employee': employee,
                'contract': contract
            }
        }

        if not self.payroll_news_id.salary_rule_id:
            return False

        rule = self.payroll_news_id.salary_rule_id

        localdict.update({
            'result': None,
            'result_qty': 1.0,
            'result_rate': 100})

        if rule._satisfy_condition(localdict):
            amount, qty, rate = rule._compute_rule(localdict)
            tot_rule = amount * qty * rate / 100.0
            return tot_rule
        return False

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.payroll_news_id and \
           (not self.payroll_news_id.payroll_structure_id.id or
                not self.payroll_news_id.salary_rule_id.id):
            self.employee_id = False
            raise UserError(_("Please add structure and salary rule."))

        amount = self._get_amount_compute_rule()

        if not amount:
            return {}
        self.amount = amount

    def _get_number_of_days(self, date_from, date_to):
        res = date_to - date_from
        w_days = self.employee_id._get_work_days_data(date_from, date_to)
        l_days = self.employee_id._get_leave_days_data(date_from, date_to)

        d_days = int(w_days['days']+l_days['days'])
        h_hrs = d_days * 24 + res.seconds/3600

        return dict(
            days=d_days,
            hours=h_hrs
        )

    def _get_calendar_number_of_days(self, date_start, date_end):
        """
            Returns a float equals to the timedelta between two
            dates given as string.
        """
        work_days = self.payroll_news_id.condition_holiday or 'none'

        date_from = fields.Datetime.from_string(date_start)
        date_to = fields.Datetime.from_string(date_end)
        date_to = date_to.replace(hour=23, minute=59)

        compute_leaves = (work_days == 'work_days') or False
        if self.employee_id:
            if work_days == 'none':
                return self._get_number_of_days(date_from, date_to)

            if compute_leaves:
                return self.employee_id._get_work_days_data(date_from, date_to)
            return self.employee_id._get_leave_days_data(date_from, date_to)

        today_hours = self.env.company.resource_calendar_id\
            .get_work_hours_count(
                datetime.combine(date_from.date(), time.min),
                datetime.combine(date_from.date(), time.max),
                compute_leaves)

        hours = self.env.company.resource_calendar_id.\
            get_work_hours_count(date_from, date_to)

        return {'days': hours / (today_hours or HOURS_PER_DAY), 'hours': hours}

    @api.onchange('employee_id')
    def _onchange_leave_dates(self):
        if self.date_from and self.date_to:
            self.quantity = self._get_calendar_number_of_days(
                self.date_from,
                self.date_to)['days']

    def _get_base_local_dict(self):
        return {
            'float_round': float_round
        }

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
        result = super(HrEmployeePayrollNews, self).create(vals)
        if result.payroll_news_id:
            msg = self._message_post_create_line(vals.copy())
            result.payroll_news_id.message_post(body=msg)
        return result

    @api.constrains('quantity')
    def _check_float_items(self):
        for record in self:
            if not record.quantity > 0:
                raise ValidationError(
                    _('Error! The field Quantity must be \
                     greater than zero.'))

    def _message_post_create_line(self, vals):
        if vals.get('payroll_news_id', False):
            del(vals['payroll_news_id'])

        tracked_fields = self.env['hr.employee.payroll.news'].fields_get(
            vals.keys())
        msg = "<b>" + _("The employee payroll news is created") + "</b><ul>"
        for elements in vals.keys():
            new_val = vals[elements]
            if tracked_fields[elements]['type'] == 'many2one':
                new_val = self.env['hr.employee'].browse(
                    vals[elements]).name
            msg += "<li> %s: %s" % (
                tracked_fields[elements]['string'],
                new_val)
        msg += "</ul>"
        return msg

    def _message_post_delete_line(self):
        msg = ""
        for record in self:
            old_values = {
                'employee_id': record.employee_id.name,
                'quantity': record.quantity,
                'amount': record.amount,
                'total': record.quantity*record.amount,
            }
            tracked_fields = record.env['hr.employee.payroll.news'].fields_get(
                old_values.keys())
            msg += "<b>" + _("The employee payroll news (%s) \
                has been deleted.") % (record.id) + "</b><ul>"
            for elements in old_values.keys():
                msg += "<li> %s: %s" % (
                    tracked_fields[elements]['string'],
                    old_values[elements])
            msg += "</ul>"
        return msg

    def _message_post_update_line(self, values):
        if values.get('payroll_news_id', False):
            payroll_news_id = values.get('payroll_news_id')
            del(values['payroll_news_id'])
        if len(values.keys()) == 0:
            return ''
        msg = ""
        for record in self:
            old_values = {
                'quantity': record.quantity,
                'amount': record.amount,
                'employee_id': record.employee_id.name
            }
            tracked_fields = record.env['hr.employee.payroll.news'].fields_get(
                old_values.keys())
            msg += "<b>" + _("The employee payroll news (%s) has \
                been updated.") % (record.id) + "</b><ul>"
            for elements in values.keys():
                if not old_values.get(elements, False):
                    continue
                new_val = values[elements]
                if tracked_fields[elements]['type'] == 'many2one':
                    new_val = record.env['hr.employee'].browse(
                        values[elements]).name
                msg += "<li> %s: %s -> %s" % (
                    tracked_fields[elements]['string'],
                    old_values[elements],
                    new_val)

            quantity = values.get('quantity') or record.quantity
            amount = values.get('amount') or record.amount
            msg += "<li> %s: %s" % (_("Total"), quantity*amount)

            msg += "</ul>"
        return msg

    def write(self, vals):
        result = super(HrEmployeePayrollNews, self).write(vals)
        if self.payroll_news_id:
            msg = self._message_post_update_line(vals.copy())
            self.payroll_news_id.message_post(body=msg)
        return result

    def unlink(self):
        if self.payroll_news_id:
            msg = self._message_post_delete_line()
            self.payroll_news_id.message_post(body=msg)
        return super(HrEmployeePayrollNews, self).unlink()
