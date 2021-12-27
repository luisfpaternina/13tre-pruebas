from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.tools.misc import format_date
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging


class HrPayrollEmployeeWizard(models.TransientModel):
    _name = 'hr.payroll.news.wizard'
    _description = "Wizard: Quick Registration of Attendees to Sessions"

    def _default_payroll_structure_id(self):
        structure_id = self.env['hr.payroll.structure'].search([
            ('type_id', '!=', False), ('type_id.is_novelty', '=', True)],
            limit=1).id
        return structure_id

    name = fields.Char(required=True, size=40, default="")
    description = fields.Text()
    date_deadline = fields.Date(string='Deadline', invisible=1)
    date_start = fields.Date(
        string='Initial date',
        required=True,
        default=datetime.now().strftime('%Y-%m-01'))
    date_end = fields.Date(
        string='End date',
        required=True,
        default=str(datetime.now() + relativedelta(
            months=+1, day=1, days=-1))[:10])
    user_id = fields.Many2one(
        'res.users',
        string='Assigned to',
        default=lambda self: self.env.uid,
        required=True)
    quantity = fields.Float(string='Units', default=1.0, required=True)
    amount = fields.Float(
        string='Quantity',
        required=True,
        digits="Payroll Rate")
    total = fields.Float(
        compute='_compute_total',
        string='Total quantity',
        required=True)

    employee_ids = fields.Many2many(
        'hr.employee',
        required=True,
        string="Employees",
        help='Select corresponding Employee')

    payroll_structure_id = fields.Many2one(
        'hr.payroll.structure',
        string='Payroll Structure',
        domain="[('type_id', '!=', False), ('type_id.is_novelty', '=', True)]",
        default=_default_payroll_structure_id,
        required=True)

    salary_rule_id = fields.Many2one(
        'hr.salary.rule',
        string='Salary rule',
        domain="[('struct_id', '=', payroll_structure_id)]",
        required=True)

    @api.depends('quantity', 'amount')
    def _compute_total(self):
        for line in self:
            line.total = float(line.quantity) * line.amount

    def add_employees_action(self):
        self.ensure_one()
        default_model = self.env.context.get('default_parent_model', False)
        _id = self.env.context.get('active_id', False)
        if _id and default_model:
            for line in self.employee_ids:
                self.env[default_model].create({
                    'payroll_news_id': _id,
                    'employee_id': line.id,
                    'quantity': self.quantity,
                    'amount': self.amount,
                })

        return {'type': 'ir.actions.act_window_close'}

    def add_novelty_employee_action(self):
        self.ensure_one()
        if self.env.context.get('default_model') and \
           self.env.context.get('employee_ids'):
            default_model = self.env.context.get('default_model')
            logging.Logger(default_model)
            _ids = self.env.context.get('employee_ids')
            record = self.env['hr.employee'].search(
                [('id', 'in', _ids)],
                limit=1)

            if record.id:
                if self.env.context.get('default_parent_model'):
                    str_model = self.env.context.get('default_parent_model')
                    line = self.env[str_model].create({
                        "quantity": self.quantity,
                        "payroll_news_id": False,
                        "employee_id": record.id,
                        "amount": self.amount,
                    })
                    logging.Logger(line)
                    ctx = dict(
                        name=self.name,
                        description=self.description,
                        date_deadline=self.date_deadline,
                        date_start=self.date_start,
                        date_end=self.date_end,
                        user_id=self.user_id.id,
                        payroll_structure_id=self.payroll_structure_id.id,
                        salary_rule_id=self.salary_rule_id.id,
                        employee_payroll_news_ids=[line.id])
                    self.env[default_model].create(ctx)

        return {'type': 'ir.actions.act_window_close'}
