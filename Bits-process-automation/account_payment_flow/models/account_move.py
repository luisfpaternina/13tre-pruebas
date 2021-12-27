# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    payment_flow_id = fields.Many2one(
        'account.payment.flow',
        readonly=True,
        string='Payment flow',
        copy=False
    )

    allowed_payment = fields.Boolean(
        string='Computed',
        compute='_compute_allowed_payment'
    )

    def action_invoice_payment_flow(self):
        return self.env['account.payment.flow']\
            .with_context(
                active_ids=self.ids,
                active_movel='account.move',
                active_id=self.id,
                invoice_name=self.name)\
            ._action_register_payment_flow()

    def _compute_allowed_payment(self):
        for record in self:
            allowed_stage = self.env\
                .ref('account_payment_flow.stage_payment_flow_3').id
            current_stage = record.payment_flow_id.stage_id

            record.allowed_payment = allowed_stage == current_stage.id

    # def post(self):
    #     res = super(AccountMove, self).post()
    #     # print('que devuelve: ', res)
    #     # print('################### Se registra pago. ', self)
    #     next_stage = self.env\
    #         .ref('account_payment_flow.stage_payment_flow_4').id

    #     for record in self:
    #         # print('===================== flujo de pago :: ',
    #  record.payment_flow_id)
    #         record.payment_flow_id.write({
    #             'stage_id': next_stage
    #         })
