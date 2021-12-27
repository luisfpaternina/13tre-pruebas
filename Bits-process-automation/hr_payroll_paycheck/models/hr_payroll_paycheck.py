# -*- coding: utf-8 -*-

from contextlib import contextmanager
import locale
import logging
from odoo.http import request
from datetime import datetime
from odoo import models, fields, api, _
from odoo.tools.misc import formatLang, format_date, get_lang
from werkzeug.urls import url_encode

_logger = logging.getLogger(__name__)


class hr_payroll_paycheck(models.Model):

    _name = 'hr.payslip'
    _inherit = ['hr.payslip', 'portal.mixin']

    user_id = fields.Many2one(
        'res.users',
        string='Assigned to',
        default=lambda self: self.env.uid,
        index=True, tracking=True, required=True)

    month_payroll = fields.Char(compute="_compute_month_payroll")
    year_payroll = fields.Char(compute="_compute_year_payroll")
    text_copyright = fields.Char(compute="_compute_text_copyright")

    payslip_sent = fields.Boolean(
        default=False)

    def _round_value_payslip(self, value):
        return round(value)

    @contextmanager
    def _custom_setlocale(self):
        old_locale = locale.getlocale(locale.LC_TIME)
        # For user self.env.context['lang'] + '.utf8'
        try:
            locale.setlocale(
                locale.LC_TIME, 'es_ES.utf8')
        except locale.Error:
            _logger.info('Error when try to set locale "es_ES". Please '
                         'contact your system administrator.')
        try:
            yield
        finally:
            locale.setlocale(locale.LC_TIME, old_locale)

    @api.depends('date_from', 'date_to')
    def _compute_month_payroll(self):
        for record in self:
            date_month = record.date_from \
                if record.date_from.month == record.date_to.month \
                else datetime.now().date()
            with self._custom_setlocale():
                record.month_payroll = date_month.strftime('%B').capitalize()

    @api.depends('date_from', 'date_to')
    def _compute_year_payroll(self):
        for record in self:
            record.year_payroll = record.date_from.year \
                if record.date_from.year == record.date_to.year\
                else datetime.now().year

    @api.depends('year_payroll')
    def _compute_text_copyright(self):
        for record in self:
            record.text_copyright = str("© " + str(record.year_payroll))
            record.text_copyright += str(
                record.employee_id.address_id.parent_id.name) \
                if record.employee_id.address_id.parent_id.name \
                else ''

    def action_paycheck_sent(self):
        self.ensure_one()
        template = self.env.ref(
            'hr_payroll_paycheck.paycheck_email_template',
            raise_if_not_found=False)
        lang = get_lang(self.env)
        lang = template._render_template(template.lang, 'hr.payslip', self.id)\
            if (template and template.lang) else lang.code
        compose_form = self.env.ref(
            'hr_payroll_paycheck.view_wizard_send_paycheck',
            raise_if_not_found=False)

        ctx = dict(
            default_model='hr.payslip',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            mark_payslip_as_sent=True,
            custom_layout="mail.mail_notification_paynow",
            model_description=_('sent payroll paycheck'),
            force_email=True
        )
        return {
            'name': _('Send Payslip'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'send.email.paycheck',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    def action_payslip_print(self):
        return self.env.ref('hr_payroll_paycheck.hr_payroll_payslip_report')\
            .report_action(self)

    def _get_share_url(self, redirect=False, signup_partner=False, pid=None):
        self.ensure_one()
        r_id = self.employee_id.address_home_id.id
        auth_param = url_encode(self.employee_id.address_home_id.
                                signup_get_auth_param()[r_id])
        return self.get_portal_url(query_string='&%s' % auth_param)
