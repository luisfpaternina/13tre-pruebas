# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class PurchaseBudgetRevision(models.Model):
    _inherit = "purchase.order"
    _description = "Check budget when making request for quotation"

    def _compute_notify_email_to(self):
        group_notify = self.env.ref(
            'purchase_budget_revision.notify_budget_excess')
        emails = group_notify.users.filtered(
            lambda user: user.partner_id.email).mapped('email')
        for record in self:
            record.email_to = ", ".join(emails)

    budget_approval_state = fields.Selection([
        ('draft', 'Draft'),
        ('excess', 'Excess'),
        ('send', 'Send to budget'),
        ('approved', 'Approved'),
    ], default='draft')

    warning_message = fields.Char(readonly=True)

    email_to = fields.Char(compute="_compute_notify_email_to")

    def _validate_budget_excess(self):
        res = []
        valid = True
        localdict = dict()
        line_ref = self.env['crossovered.budget.lines']
        for line in self.order_line:
            line.is_excess_budget = line._verificate_order_line_budget()
            if line.is_excess_budget:
                valid = False
                res.append(
                    _("Some of the lines do not comply "
                      "with the verification process\n")
                )
            _id = line.crossovered_budget_line_id.id
            if not localdict.get(_id, False):
                localdict[_id] = 0
            localdict[_id] += abs(line.price_subtotal)
        for key in localdict:
            amount = localdict[key]
            line = line_ref.browse(key)
            name = line.crossovered_budget_id.name or ''
            planned_amount = abs(line.planned_amount)
            practical_amount = abs(line.practical_amount)
            total = planned_amount - practical_amount
            if amount > total:
                valid = False
                res.append(
                    _("% s. Exceeds budget: "
                      "% s / % s.") % (name, amount, total, )
                )
        return valid, res

    def button_approve(self, force=False):
        error = False
        for order in self:
            valid, res = order._validate_budget_excess()
            state = 'approved'
            if not valid:
                error = True
                order.warning_message = "\n".join(res)
                state = 'excess'
            order.write({'budget_approval_state': state})
        if error:
            return False
        order.warning_message = False
        return super(PurchaseBudgetRevision, self).button_approve(force)

    def button_confirm(self):
        error = False
        for order in self:
            valid, res = order._validate_budget_excess()
            state = 'approved'
            if not valid:
                error = True
                order.warning_message = "\n".join(res)
                state = 'excess'
            order.write({'budget_approval_state': state})

        if error:
            return False
        order.warning_message = False
        return super(PurchaseBudgetRevision, self).button_confirm()

    def action_notification_send(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        template = self.env.ref(
            'purchase_budget_revision.email_template_notify_budget_excess',
            False
        )
        compose_form = self.env.ref(
            'mail.email_compose_message_wizard_form', False)
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'purchase.order',
            'active_model': 'purchase.order',
            'active_id': self.ids[0],
            'default_res_id': self.ids[0],
            'default_use_template': bool(template),
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
            'mark_up_budget_sent': True
        })
        return {
            'name': _('Send for approved budget'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get('mark_up_budget_sent'):
            self.filtered(lambda o: o.budget_approval_state == 'excess')\
                .write({'budget_approval_state': 'send'})
        return super(
            PurchaseBudgetRevision,
            self.with_context(mail_post_autofollow=True)
        ).message_post(**kwargs)
