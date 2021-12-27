# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.tools.translate import _


class AccountMoveReversal(models.TransientModel):
    _inherit = 'account.move.reversal'
    _description = 'Account Move Reversal'

    _type = fields.Selection([
        ('credit_note', 'Credit Note'),
        ('debit_note', 'Debit Note')],
        string='Document Type'
    )

    description_code_credit = fields.Many2one(
        'l10n_co.description_code',
        string="Credit Note Concept",
        copy=False,
        domain="[('type', '=', 'credit')]",
    )
    description_code_debit = fields.Many2one(
        'l10n_co.description_code',
        string="Debit Note Concept",
        copy=False,
        domain="[('type', '=', 'debit')]",
    )

    def reverse_moves(self):
        if self.move_type in ('out_invoice', 'out_refund'):
            _ref = 'l10n_co_account_e_invoice.l10n_co_type_documents_'
            _type = self.env.ref(_ref + '5')\
                if self._type == 'credit_note'\
                else self.env.ref(_ref + '6')
            self.reason = _type.name

        if self._type == 'debit_note':
            invoice = self.debit_note_process(_type)
            return invoice

        action = super(AccountMoveReversal, self).reverse_moves()
        res_id = action.get('res_id', False)
        if res_id and self.move_type in ('out_invoice', 'out_refund'):
            move = self.env['account.move'].browse(res_id)
            credit = self.description_code_credit \
                if self._type == 'credit_note' else False
            operation_type = self.env.ref(
                'l10n_co_account_e_invoice.l10n_co_type_operations_4'
            ) if self._type == 'credit_note' else False
            move.update({
                'ei_type_document_id': _type.id or False,
                'ei_origin_id': self.move_id.id or False,
                'operation_type': operation_type,
                'description_code_credit': credit,
            })
        return action

    def debit_note_process(self, _type):
        debit_note = self.move_id.copy()
        debit_note.update(
            {
                'ei_type_document_id': _type.id or False,
                'ei_origin_id': self.move_id.id or False,
                'operation_type': self.env.ref(
                    'l10n_co_account_e_invoice.l10n_co_type_operations_7'
                ),
                'description_code_debit': self.description_code_debit,
                'journal_id': self.journal_id,
            }
        )
        return {
            'name': _('Reverse Moves'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'form',
            'res_id': debit_note.id,
        }
