# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError
import logging


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _compute_payroll_news_count(self):
        for each in self:
            _ids = self.env['hr.employee.payroll.news'].sudo().search(
                [('employee_id', '=', each.id)])
            each.payroll_news_count = len(_ids)

    payroll_news_count = fields.Integer(
        compute='_compute_payroll_news_count',
        string='# Payroll news')

    def add_novelty_action(self):
        self.ensure_one()
        compose_form = self.env.ref(
            'bits_hr_payroll_news.employee_payroll_news_wizard_form',
            raise_if_not_found=False)
        ctx = dict(
            default_model='hr.payroll.news',
            default_parent_model='hr.employee.payroll.news',
            employee_ids=self.ids,
        )
        return {
            'name': _('Create Novelty'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.payroll.news.wizard',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    def payroll_news_view(self):
        self.ensure_one()
        domain = [
            ('employee_id', '=', self.id)]
        return {
            'name': _('Payroll News'),
            'domain': domain,
            'res_model': 'hr.employee.payroll.news',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click to Create for New Documents
                        </p>'''),
            'limit': 80,
            'context': "{'default_employee_id': '%s'}" % self.id
        }
