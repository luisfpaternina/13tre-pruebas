# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools.translate import _
from odoo.exceptions import ValidationError, UserError
from werkzeug.urls import url_join
import logging

class HrEmployeeInternalRequest(models.Model):
    _name = 'hr.employee.internal.request'
    _inherit = ['mail.activity.mixin', 'mail.thread.cc']

    name = fields.Char(
        _('Internal Request Name'),
        store=True,
        translate=True)

    reason_for_rejection = fields.Char(
        'Reason for rejection',
        size=200)

    analytic_account_id = fields.Many2one(
        'account.analytic.account',
        string="Analytic account")

    approval_reason = fields.Char(
        'Approval_reason',
        size=200)

    link = fields.Char('Link', size=200)

    reason_for_cancellation = fields.Char(
        'Reason for cancellation',
        size=200)

    job_position = fields.Many2one(
        'hr.job',
        string=_('Job Position'))

    code = fields.Char(
        string="Code",
        tracking=True,
        readonly=True,
        required=True,
        copy=False,
        default='New')

    department_id = fields.Many2one(
        'hr.department',
        string="Department",
        related="job_position.department_id"
    )

    number_of_employees = fields.Integer(
        string="employee's number")

    is_internal_request = fields.Boolean(
        string="Internal request client")

    description = fields.Char(string="Description")

    internal_request_line_ids = fields.One2many(
        'hr.employee.internal.request.lines',
        'internal_request_id',
        string="Internal request lines"
    )

    job_description = fields.Html(
        string="Job description")

    tecnology_id = fields.Many2one(
        'hr.recruitment.score.technologies',
        string="Tecnology")

    job_name = fields.Char(
        string="Job name",
        related="job_position.name"
    )

    department_email = fields.Char(
        string="Email"
    )

    tecnology_name = fields.Char(
        string="Tecnology name",
        related="tecnology_id.name"
    )

    check_project = fields.Boolean(
        string="Is projects e I+D+I.",
        compute="_compute_job_position")

    check_not_project = fields.Boolean(
        string="Not Is projects e I+D+I.",
        compute="_compute_job_position_project")

    analytic_account_name = fields.Char(
        string="Account Analytic",
        related="analytic_account_id.name"
    )

    res_user_id = fields.Many2one(
        related="job_position.user_id",
        string="Responsable"
    )

    employee_name_id = fields.Many2one(
        'hr.department',
        string="Employee",
        compute="_compute_employee_name_id")
  
    job_name_id = fields.Many2one(
        'hr.job',
        string="Job",
        compute="_compute_job_name_id"
    )

    def _compute_job_name_id(self):
        job_project = self.env['hr.job'].search([('name','=','Líder de talento humano')])
        if job_project:
            self.job_name_id = job_project.id
        job_project = self.env['hr.job'].search(
            [('name', '=', 'Líder de talento humano')])
        if job_project:
            self.job_name_id = job_project.id
        else:
            self.job_name_id = False

    def _compute_employee_name_id(self):
        employee_project = self.env['hr.department'].search([('name','=','Proyectos')])
        if employee_project:
            self.employee_name_id = employee_project.id
        else:
            self.employee_name_id = False

        employee_project = self.env['hr.department'].search(
            [('name', '=', 'Proyectos')])
        if employee_project:
            self.employee_name_id = employee_project.id
        else:
            self.employee_name_id = False

    def get_users_emails(self):
        emails = []
        for record in self:
            for line in record.internal_request_line_ids:
                if line.employee_id.work_email:
                    emails.append(line.employee_id.work_email)
            formatemail = ' '.join([str(elem) for elem in emails])
            formatemail = formatemail.replace(" ", ",")
        
        return formatemail
                   
    @api.onchange('job_name', 'tecnology_name', 'analytic_account_name')
    def _onchange_internal_request_name(self):
        self.name = "%s/%s/%s" % (
            self.job_name if self.job_name else "",
            self.tecnology_name if self.tecnology_name else "",
            self.analytic_account_name if self.analytic_account_name else ""
        )
    
    @api.constrains('number_of_employees')
    def _validate_number_of_employees(self):
        if self.number_of_employees < 0:
            raise ValidationError("The number of employees cannot be negative")

    @api.constrains('number_of_employees')
    def _validate_number_of_employees(self):
        if self.number_of_employees < 0:
            raise ValidationError(_("The \
                number of employees cannot be negative"))

    @api.depends('job_position')
    def _compute_job_position(self):
        for record in self:
            record.check_project = (
                True if record.department_id and
                record.department_id[0].name == 'Proyectos' else False)

    @api.depends('job_position')
    def _compute_job_position_project(self):
        for record in self:
            record.check_not_project = (
                True if record.department_id and record.department_id[
                    0].name == 'I+D+I' else False)

    @api.model
    def create(self, vals):
        if vals.get('code', 'New') == 'New':
            vals['code'] = self.env['ir.sequence'].next_by_code(
                'internal.request') or 'New'
        result = super(HrEmployeeInternalRequest, self).create(vals)
        return result

    @api.model
    def _get_stage_default(self):
        return self._default_stage().id
    stage_id = fields.Many2one(
        'hr.employee.internal.request.stages',
        string='Stage',
        ondelete='restrict', tracking=True,
        group_expand='_get_stage_ids',
        default=_get_stage_default
    )

    @api.model
    def _get_stage_ids(self, stages, domain, order):
        return self.env['hr.employee.internal.request.stages'].search([])

    def _default_stage(self):
        return self._get_stage([('sequence', '=', 1)])

    def _get_stage(self, domain):
        return self.env['hr.employee.internal.request.stages'].search(
            domain, limit=1, order='sequence')

    ####
    # TODO: US - 8840
    def _validate_privileges(self, action_name):
        restrict_action = self.env['ir.actions.restrict'].search([
            ('model', '=', self._name),
            ('action_name', '=', action_name)
        ])

        if restrict_action:
            restrict_action.validate_user_groups()

    def _update_state(self, stage):
        self.stage_id = stage

    def action_request_approve(self):
        self._validate_privileges('action_ir_human_resource')
        context = self.env.context.copy()
        context['ir_stage_id'] = self._get_stage(
            domain=[('sequence', '=', 3)]).id

        return dict(
            name=_('Approve internal request'),
            res_model='hr.employee.internal.request.wizard',
            view_mode='form',
            view_id=self.env.ref(
                'hr_employee_internal_request.'
                'hr_employee_approve_ir_wizard').id,
            context=context,
            target='new',
            type='ir.actions.act_window')
        # for request in self:
        #     request._update_state(
        #         request._get_stage(domain=[('sequence', '=', 3)]))

    def action_request_return(self):
        self._validate_privileges('action_ir_human_resource')
        context = self.env.context.copy()
        context['ir_stage_id'] = self._get_stage(
            domain=[('sequence', '=', 2)]).id

        return dict(
            name=_('Return internal request'),
            res_model='hr.employee.internal.request.wizard',
            view_mode='form',
            view_id=self.env.ref(
                'hr_employee_internal_request.'
                'hr_employee_internal_request_wizard').id,
            context=context,
            target='new',
            type='ir.actions.act_window')

    def action_request_cancel(self):
        context = self.env.context.copy()
        context['ir_stage_id'] = self._get_stage(
            domain=[('sequence', '=', 6)]).id

        return dict(
            name=_('Cancel internal request'),
            res_model='hr.employee.internal.request.wizard',
            view_mode='form',
            view_id=self.env.ref(
                'hr_employee_internal_request.'
                'hr_employee_cancel_ir_wizard').id,
            context=context,
            target='new',
            type='ir.actions.act_window')

    def action_request_sent(self):
        self._validate_privileges('action_ir_applicant')

        for request in self:
            request.stage_id = request._default_stage()

    def action_request_process(self):
        self._validate_privileges('action_ir_human_resource')

        for request in self:
            request._update_state(
                request._get_stage(domain=[('sequence', '=', 4)]))

    def action_request_process_by_publish(self):
        for ir_item in self:
            if ir_item.stage_id == ir_item\
                    ._get_stage(domain=[('sequence', '=', 3)]):
                ir_item._update_state(
                    ir_item._get_stage(domain=[('sequence', '=', 4)]))

    def _get_partners_from_job(self, stage):
        job_ids = stage.email_profile_ids.ids

        if not job_ids and stage == self._default_stage():
            _("no mails with charge have been configured for this stage")

        employees = self.env['hr.employee'].search([
            ('job_id', 'in', job_ids),
            ('address_home_id', '!=', False),
            ('address_home_id.email', '!=', False)
        ])

        emails = [p.email for p in [e.address_home_id for e in employees]]

        if not emails and not stage.is_cancelled:
            emails = [self.create_uid.email]

        if stage.is_cancelled \
            and self.create_uid.email not in emails\
                and self.env.user != self.create_uid:
            emails.append(self.create_uid.email)

        if self.env.user.email in emails:
            emails.remove(self.env.user.email)

        return emails

    def get_model_url(self, params):
        params = tuple(
            ['%s=%s' % (v, params.get(v)) for v in list(params.keys())])
        return ('web#%s&%s&%s&%s&%s&%s' % params)

    def _generate_link(self):
        base_url = self.env['ir.config_parameter']\
            .sudo().get_param('web.base.url')

        action_id = self.env.ref(
            'hr_employee_internal_request.'
            'action_hr_employee_internal_request').id

        menu_id = self.env.ref(
            'hr_recruitment.menu_hr_recruitment_root').id

        params = dict(
            id=self.id,
            action=action_id,
            model=self._name,
            view_type='form',
            cids=self.env.company.id,
            menu_id=menu_id)

        return url_join(base_url, self.get_model_url(params))

    # ---------------------------------------------------
    # Mail gateway
    # ---------------------------------------------------
    def _track_template(self, changes):
        res = super(HrEmployeeInternalRequest, self)._track_template(changes)
        template = self.stage_id.template_id
        emails = self._get_partners_from_job(self.stage_id)

        if not self.link:
            self.link = self._generate_link()

        template.write({
            'email_to': ','.join(emails)
        })

        if 'stage_id' in changes and template:
            res['stage_id'] = (template, {
                'auto_delete_message': True,
                'subtype_id': self.env['ir.model.data']
                .xmlid_to_res_id('mail.mt_note'),
                'email_layout_xmlid': 'mail.mail_notification_light'
            })

        return res


class HrEmployeeInternalRequestLines(models.Model):
    _name = 'hr.employee.internal.request.lines'

    internal_request_id = fields.Many2one(
        'hr.employee.internal.request',
        string="Internal request")

    internal_appraisal_id = fields.Many2one(
        'hr.recruitment.appraisal.request',
        string="Appraisal")

    employee_id = fields.Many2one(
        related="internal_appraisal_id.employee_id",
        string="Evaluator")
