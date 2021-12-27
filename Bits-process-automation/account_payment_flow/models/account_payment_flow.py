# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class AccountPaymentFlow(models.Model):
    _name = 'account.payment.flow'
    _description = _('account_payment_flow.account_payment_flow')
    _inherit = ['portal.mixin', 'mail.thread.cc',
                'mail.activity.mixin', 'rating.mixin']

    name = fields.Char()

    @api.model
    def _get_partner(self):
        return self._default_stage().partner_id

    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 default=lambda self: self.env.company)
    company_currency_id = fields.Many2one(related='company_id.currency_id')

    amount_to_payment = fields.Monetary(
        string="Amount To Payment",
        currency_field='currency_id')

    currency_id = fields.Many2one(
        'res.currency',
        string=_('Currency')
    )

    partner_id = fields.Many2one(
        'res.partner',
        string="Assigned to",
        required=True,
        default=_get_partner)
    journal_id = fields.Many2one(
        'account.journal',
        string='Journal',
        domain=[('type', '=', 'bank')])
    payment_instructions = fields.Text(
        'Payment instructions', size=2000)

    payment_method_id = fields.Many2one(
        'account.payment.method',
        string='Payment Method')

    def _compute_payment_check(self):
        self.payment_method_check = True
    payment_method_check = fields.Boolean(
        'Is first stage',
        compute=_compute_payment_check
    )
    invoice_id = fields.Many2one(
        string='Invoice',
        comodel_name='account.move',
    )

    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Important')
    ], default='0', index=True)
    color = fields.Integer('Color Index')
    kanban_state = fields.Selection([
        ('normal', 'Grey'),
        ('done', 'Green'),
        ('blocked', 'Red')
    ], string='State Kanban', default='normal', required=True)

    purchase_order = fields.Boolean(
        string='Purchase Order',
        compute="_compute_purchase_order_invoice"
    )

    @api.depends('journal_id')
    def _compute_purchase_order_invoice(self):
        for record in self:
            order = self.env['purchase.order'].search(
                [('invoice_ids', 'in', (record.env.context.get('active_id')))])
            record.purchase_order = True if order else False

    @api.model
    def _get_stage_default(self):
        return self._default_stage().id
    stage_id = fields.Many2one(
        'account.payment.flow.stage',
        string='Stage',
        ondelete='restrict', tracking=True,
        group_expand='_get_stage_ids',
        default=_get_stage_default
    )

    @api.model
    def _get_stage_ids(self, stages, domain, order):
        return self.env['account.payment.flow.stage'].search([])

    def _default_stage(self):
        return self._get_stage([('sequence', '=', 1)])

    def _get_stage(self, domain):
        return self.env['account.payment.flow.stage'].search(
            domain, limit=1, order='sequence')

    @api.onchange('journal_id')
    def _onchange_field(self):
        payment_methods = self.journal_id.outbound_payment_method_ids

        domain = {
            'payment_method_id': [
                ('payment_type', '=', 'outbound'),
                ('id', 'in', payment_methods.ids)
            ]
        }

        return {'domain': domain}

    def _action_register_payment_flow(self):
        active_ids = self.env.context.get('active_ids')
        if not active_ids:
            return ''

        invoice = self.env['account.move'].browse(
            self.env.context.get('active_id'))

        name_ref = invoice.name if not invoice.ref else invoice.ref

        context = self.env.context.copy()
        context['default_name'] = "{0}-{1}".format(
            name_ref, invoice.partner_id.name)

        return {
            'name': _('Register Payment Flow'),
            'res_model': 'account.payment.flow',
            'view_mode': 'form',
            'view_id': self.env
            .ref('account_payment_flow.'
                 'account_payment_flow_wizard').id,
            'context': context,
            'target': 'new',
            'type': 'ir.actions.act_window'
        }

    def register_record(self):
        invoice = self.env['account.move'].browse(
            self.env.context.get('active_id'))

        name_ref = invoice.name if not invoice.ref else invoice.ref

        self.write({
            'name': "{0}-{1}".format(name_ref, invoice.partner_id.name),
            'invoice_id': invoice.id,
            'amount_to_payment': abs(invoice.amount_residual),
        })

        invoice.write({
            'payment_flow_id': self.id
        })

        return True

    def _validate_groups(self, stage):
        if not stage.team_ids:
            return

        user_logged = self.env.user
        user_in_team = next((
            team for team
            in stage.team_ids
            if user_logged in team.group.users
        ), False)

        if user_in_team:
            return

        raise ValidationError(
            _("you don't have privileges"
                " to modify this stage"))

    def _change_assigned_to(self, stage):
        if not stage.partner_id:
            return

        return stage.partner_id.id

    def _valid_previus_stage(self, stage):
        invoice = self.env['account.move'].search([
            ('payment_flow_id', '=', self.id)
        ], limit=1)

        if (invoice.invoice_payment_state == 'paid'
                and stage.sequence < self.stage_id.sequence):

            raise ValidationError(
                _("You cannot return the stage "
                  "as the invoice is paid"))

        return

    def write(self, vals):
        if vals.get('stage_id'):
            stage = self.env['account.payment.flow.stage']\
                .browse(vals.get('stage_id'))

            for flow in self:
                flow._validate_groups(stage)
                flow._valid_previus_stage(stage)
                partner_id = flow._change_assigned_to(stage)

                if partner_id:
                    vals['partner_id'] = partner_id
        return super(AccountPaymentFlow, self).write(vals)

    # ---------------------------------------------------
    # Mail gateway
    # ---------------------------------------------------

    def _track_template(self, changes):
        res = super(AccountPaymentFlow, self)._track_template(changes)
        account_payment_flow = self[0]
        if 'stage_id' in changes and account_payment_flow.stage_id.template_id:
            res['stage_id'] = (account_payment_flow.stage_id.template_id, {
                'auto_delete_message': True,
                'subtype_id': self.env['ir.model.data']
                .xmlid_to_res_id('mail.mt_note'),
                'email_layout_xmlid': 'mail.mail_notification_light'
            })
        return res
