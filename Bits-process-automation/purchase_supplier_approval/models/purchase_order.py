# -*- coding: utf-8 - *-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    partner_id = fields.Many2one('res.partner', required=False)
    director_id = fields.Many2one('res.partner')

    approved_by_director = fields.Boolean(
        'Approved by director',
        default=False,
        tracking=True)

    def write(self, vals):
        response = super(PurchaseOrder, self).write(vals)

        if self.state == 'purchase':
            if len(self.order_line) == 0:
                raise ValidationError(
                    _('The purchase order must have products assigned'))

            if not self.approved_by_director:
                raise ValidationError(
                    _('the purchase order must be approved by the principal'))

        return response

    def get_restrict_action_move(self, action_name):
        restrict_action = self.env['ir.actions.restrict'].search([
            ('model', '=', self._name),
            ('action_name', '=', action_name)
        ])
        if restrict_action:
            restrict_action.validate_user_groups()

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get('mark_rfq_as_sent'):
            self.filtered(lambda o: o.state == 'draft').write(
                {'state': 'to approve'})

        return super(PurchaseOrder,
                     self.with_context(mail_post_autofollow=True)
                     ).message_post(**kwargs)

    def action_approve_oc(self):
        self.get_restrict_action_move('action_approve_oc')
        self.approved_by_director = True

    def action_rfq_send(self):
        response = super(PurchaseOrder, self).action_rfq_send()

        # ir_model_data = self.env['ir.model.data']
        # self.ensure_one()
        if self.state == 'draft':
            template = self.env.ref(
                'purchase_supplier_approval.email_template_approved_purchase',
                raise_if_not_found=False)

            response['context'].update({
                'default_use_template': bool(template),
                'default_template_id': template.id
            })

            director = self.env['hr.employee'].search([
                ('job_id.name', 'ilike', 'dirección comercial')
            ], limit=1)

            partner = director.address_id

            subtype = self.env['mail.message.subtype'].search([
                ('id', '=', '1')
            ])

            mail_follower = self.env['mail.followers'].search([
                ('res_id', '=', self.id),
                ('partner_id', '=', partner.id)
            ], limit=1)

            if not mail_follower:
                self.env['mail.followers'].create({
                    'res_model': 'purchase.order',
                    'res_id': self.id,
                    'partner_id': partner.id,
                    'subtype_ids': [
                        (subtype.id)
                    ]
                })

        return response
