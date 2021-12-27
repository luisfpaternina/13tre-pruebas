# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools.misc import formatLang, format_date, get_lang
from werkzeug.urls import url_encode
from ast import literal_eval


class HrPayrollApproval(models.Model):
    _name = 'hr.payslip'
    _inherit = ['hr.payslip', 'mail.thread', 'portal.mixin']

    user_id = fields.Many2one(
        'res.users',
        copy=False,
        tracking=True,
        string='Salesperson',
        default=lambda self: self.env.user
    )

    struct_id = fields.Many2one(
        track_visibility='onchange',
        states={},
        readonly=False
    )
    name = fields.Char(track_visibility='onchange', states={}, readonly=False)
    number = fields.Char(
        track_visibility='onchange',
        states={},
        readonly=False)
    employee_id = fields.Many2one(
        track_visibility='onchange',
        states={},
        readonly=False)
    date_from = fields.Date(
        track_visibility='onchange',
        states={},
        readonly=False)
    date_to = fields.Date(
        track_visibility='onchange',
        states={},
        readonly=False)
    state = fields.Selection(
        track_visibility='onchange',
        states={},
        readonly=False)
    line_ids = fields.One2many(
        track_visibility='onchange',
        states={},
        readonly=False)
    company_id = fields.Many2one(
        track_visibility='onchange',
        states={},
        readonly=False)
    worked_days_line_ids = fields.One2many(
        track_visibility='onchange', states={}, readonly=False)
    input_line_ids = fields.One2many(
        track_visibility='onchange',
        states={},
        readonly=False)
    paid = fields.Boolean(
        track_visibility='onchange',
        states={},
        readonly=False)
    note = fields.Text(track_visibility='onchange', states={}, readonly=False)
    contract_id = fields.Many2one(
        track_visibility='onchange',
        states={},
        readonly=False)
    credit_note = fields.Boolean(
        track_visibility='onchange',
        states={},
        readonly=False)
    payslip_run_id = fields.Many2one(
        track_visibility='onchange',
        states={},
        readonly=False)
    compute_date = fields.Date(
        track_visibility='onchange',
        states={},
        readonly=False)
    basic_wage = fields.Monetary(
        track_visibility='onchange',
        states={},
        readonly=False)
    net_wage = fields.Monetary(
        track_visibility='onchange',
        states={},
        readonly=False)
    currency_id = fields.Many2one(
        track_visibility='onchange',
        states={},
        readonly=False)
    warning_message = fields.Char(
        track_visibility='onchange',
        states={},
        readonly=False)

    general_state = fields.Selection(
        [
            ('none', 'None'),
            ('approved', 'Approved'),
            ('disapproved', 'Disapproved'),
            ('not sent', 'Not sent for approval'),
            ('sent', 'Sent for approval'),
            ('rejected', 'Sent for approval and rejected')
        ],
        default='not sent',
        track_visibility='onchange'
    )

    def action_payslip_draft(self):
        self.general_state = 'not sent'
        super(HrPayrollApproval, self).action_payslip_draft()
        self.update_state_batch()

    def get_restrict_action(self, action_name):
        restrict_actions = self.env['ir.actions.restrict'].search(
            [('model', '=', self._name), ('action_name', '=', action_name)])
        if restrict_actions:
            restrict_actions.validate_user_groups()

    def not_approve_payroll(self):
        for record in self:
            record.get_restrict_action('not_approve_payroll')
            if record.general_state == 'sent' and record.state == 'verify':
                record.general_state = 'rejected'
                self.update_state_batch()
            else:
                raise ValidationError(
                    _(
                        'You cannot reject a payroll when it has not' +
                        ' been submitted for approval or is approved'
                    )
                )

    def approve_payroll(self):
        for record in self:
            record.get_restrict_action('approve_payroll')
            if record.state == 'verify' and record.general_state == 'sent':
                record.general_state = 'approved'
            else:
                raise ValidationError(
                    _(
                        "You cannot approve a payroll that does not have" +
                        " a general status 'Sent for approval' or that" +
                        " has already been approved"
                    )
                )
            self.update_state_batch()

    def action_payslip_cancel(self):
        for record in self:
            if record.general_state != 'approved':
                super(HrPayrollApproval, self).action_payslip_cancel()
                record.general_state = 'disapproved'
            else:
                raise ValidationError(
                    _(
                        'You cannot cancel a nominee that has already' +
                        ' been approved'
                    )
                )
            self.update_state_batch()

    def action_payslip_done(self):
        for record in self:
            if record.general_state == 'approved':
                super(HrPayrollApproval, self).action_payslip_done()
            else:
                raise ValidationError(
                    _(
                        "To pass the payroll to the 'Done' state, the " +
                        "'General state' must be 'Approved'"
                    )
                )

    def write(self, vals):
        message = _('The payroll is approved, for this reason it ' +
                    'cannot be modified')
        for record in self:
            if record.general_state == 'approved':
                if 'date' in vals and len(vals) == 1:
                    raise ValidationError(message)
        return super(HrPayrollApproval, self).write(vals)

    def action_payroll_approval_sent(self):
        self.ensure_one()
        template = self.env.ref(
            'hr_payroll_approval.approval_email_template',
            raise_if_not_found=False
        )
        lang = get_lang(self.env)
        if template and template.lang:
            lang = template._render_template(
                template.lang,
                'hr.payslip',
                self.id
            )
        else:
            lang = lang.code
        compose_form = self.env.ref(
            'hr_payroll_approval.view_wizard_send_email_payroll_approval',
            raise_if_not_found=False
        )
        ctx = dict(
            default_model='hr.payslip',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            custom_layout="mail.mail_notification_paynow",
            model_description=_('sent payroll approval'),
            force_email=True
        )
        return {
            'name': ('Send Payroll Approval'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'send.email.payroll.approval',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    def _get_jobs_for_email(self):
        str_jobs_ids = self.env['ir.config_parameter'].sudo()\
            .get_param('many2many.emails_job_ids')

        if not str_jobs_ids:
            return False

        return self.env['hr.job'].search([
            ('id', 'in', literal_eval(str_jobs_ids))
        ])

    def search_financial_administrative_director(self):
        jobs = self._get_jobs_for_email()
        if not jobs:
            raise ValidationError(
                _('Jobs for payroll approval not configured'))

        job_names = [job.name for job in jobs]
        employees = self.env['hr.employee'].search([
            ('job_id.name', 'in', job_names)
        ])

        partners = self.env['res.partner'].search([
            ('id', 'in', [emp.address_home_id.id for emp in employees])
        ])

        subtype = self.env['mail.message.subtype'].search([
                ('id', '=', '1')
            ])

        return partners, subtype

    def send_approval(self):
        partners, subtype = self.search_financial_administrative_director()
        for record in self:
            if record.state == 'verify':
                mail_followers = self.env['mail.followers'].search([
                        ('res_model', '=', 'hr.payslip'),
                        ('res_id', '=', record.id)
                    ])

                c_foll = [old.partner_id.id for old in mail_followers]
                add_partners = list(set(partners.ids) - set(c_foll))
                if add_partners:
                    new_followers = [dict(
                        res_model='hr.payslip',
                        res_id=record.id,
                        partner_id=partner_id,
                        subtype_ids=[(subtype.id)])
                            for partner_id in add_partners]

                    self.env['mail.followers'].create(new_followers)
                    record.general_state = 'sent'
                elif record.general_state == 'sent':
                    raise ValidationError(
                        _(
                            "The payroll has already been " +
                            "submitted for approval"
                        )
                    )
                elif record.general_state == 'approved':
                    raise ValidationError(
                        _(
                            "You cannot submit for approval " +
                            "a payroll that is already approved"
                        )
                    )
                else:
                    record.general_state = 'sent'
            else:
                raise ValidationError(
                    _("A payroll with a status other than 'Verify' cannot " +
                      "be submitted for approval")
                )
            self.update_state_batch()
        return True

    def update_state_batch(self):
        if self.payslip_run_id:
            self.payslip_run_id._update_states()

    def action_payslip_custom_print(self):
        return self.env.ref(
            'hr_payroll_paycheck.hr_payroll_payslip_report'
        ).report_action(self)

    def _get_share_url(self, redirect=False, signup_partner=False, pid=None, share_token=True):
        """Override for sales order.

        If the SO is in a state where an action is required from the partner,
        return the URL with a login token. Otherwise, return the URL with a
        generic access token (no login).
        """
        self.ensure_one()
        if self.state not in ['done']:
            auth_param = url_encode(
                self.employee_id.address_id.signup_get_auth_param()[
                    self.employee_id.address_id.id
                ]
            )
            return self.get_portal_url(query_string='&%s' % auth_param)
        return super(HrPayrollApproval, self)._get_share_url(
            redirect,
            signup_partner,
            pid,
            share_token
        )

    def compute_sheet_mass(self):
        for record in self:
            record.compute_sheet()


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    internal_state = fields.Selection(
        [
            ('approved', 'Approved'),
            ('disapproved', 'Disapproved'),
            ('not sent', 'Not sent for approval'),
            ('sent', 'Sent for approval'),
            ('rejected', 'Sent for approval and rejected')
        ],
        default='not sent'
    )

    def action_validate(self):
        for record in self:
            if record.internal_state == 'approved':
                super(HrPayslipRun, self).action_validate()
            else:
                raise ValidationError(
                    _(
                        "the batch cannot be passed to the 'Done' state if " +
                        "its internal state is different from 'Approved'"
                    )
                )

    def action_draft(self):
        self.mapped('slip_ids').filtered(
            lambda slip: slip.general_state in ['disapproved']
        ).action_payslip_draft()
        self.mapped('slip_ids').filtered(
            lambda slip: slip.general_state in ['not sent']
        ).compute_sheet()
        return self.write({'state': 'draft'})

    def approve_batch(self):
        self.mapped('slip_ids').filtered(
            lambda slip: slip.general_state == 'sent'
        ).approve_payroll()

    def disapprove_batch(self):
        self.mapped('slip_ids').filtered(
            lambda slip: slip.general_state == 'sent'
        ).not_approve_payroll()

    def _update_states(self):
        count_general = 0
        count_sent = 0
        count_rejected = 0
        count_disapproved = 0
        count_approved = 0
        count_not_sent = 0
        for slip in self.mapped('slip_ids'):
            count_general += 1
            if slip.general_state == 'sent':
                count_sent += 1
            elif slip.general_state == 'rejected':
                count_rejected += 1
            elif slip.general_state == 'disapproved':
                count_disapproved += 1
            elif slip.general_state == 'approved':
                count_approved += 1
            elif slip.general_state == 'not sent':
                count_not_sent += 1
        if count_rejected > 0:
            self.internal_state = 'rejected'
        elif count_not_sent > 0:
            self.internal_state = 'not sent'
        elif count_sent > 0:
            self.internal_state = 'sent'
        elif count_disapproved > 0:
            self.internal_state = 'disapproved'
        else:
            self.internal_state = 'approved'
