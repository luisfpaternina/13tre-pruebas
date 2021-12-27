# coding: utf-8

from odoo import models, fields, models, api, _
from odoo.exceptions import ValidationError


class SupportFilesSend(models.TransientModel):
    _name = "support.files.send"
    _description = _(
        'management of sending support files to the technology provider'
    )

    invoice_id = fields.Many2one(
        'account.move'
    )
    message = fields.Char(
        compute="_compute_message_wizard",
    )
    attachment_ids = fields.Many2many('ir.attachment', string="Attach a file")

    line_ids = fields.One2many(
        'wizard.custom.field.line',
        inverse_name='parent_id'
    )

    @api.model
    def default_get(self, fields):
        res = super(SupportFilesSend, self).default_get(fields)
        _ids = self.env.context.get('active_ids', [])
        move_ids = self.env['account.move'].browse(_ids) \
            if self.env.context.get('active_model') == 'account.move' \
            else self.env['account.move']
        res['invoice_id'] = move_ids[0].id if move_ids else False
        return res

    @api.depends('invoice_id')
    def _compute_message_wizard(self):
        self.message = self._context.get('message', '')

    @api.onchange('attachment_ids')
    def _get_invoice_id(self):
        self.invoice_id = self._context.get('invoice_id')

    @api.depends('invoice_id')
    def _get_default_reconcile_line_ids(self):
        types = ('receivable', 'payable')
        pay_term_line_ids = self.invoice_id.line_ids.filtered(
            lambda line: line.account_id.user_type_id.type in types)

        domain = [
            ('account_id', 'in', pay_term_line_ids.mapped('account_id').ids),
            '|', ('move_id.state', '=', 'posted'), '&',
            ('move_id.state', '=', 'draft'),
            ('journal_id.post_at', '=', 'bank_rec'),
            ('partner_id', '=', self.invoice_id.commercial_partner_id.id),
            ('reconciled', '=', False), '|', ('amount_residual', '!=', 0.0),
            ('amount_residual_currency', '!=', 0.0)]

        extend = [('credit', '>', 0), ('debit', '=', 0)] \
            if self.invoice_id.is_inbound() \
            else [('credit', '=', 0), ('debit', '>', 0)]
        domain.extend(extend)
        lines = self.env['account.move.line'].search(domain)
        return domain

    reconcile_line_ids = fields.Many2many(
        'account.move.line',
        string='Journal Items',
        domain=_get_default_reconcile_line_ids,
    )

    @api.onchange('invoice_id')
    def _onchange_invoice_id(self):
        return {
            'domain': {
                'reconcile_line_ids': self._get_default_reconcile_line_ids()
            }
        }

    def create_account_extra_ref(self, vals):
        return self.env['account.extra.refs'].create(vals)

    def action_post_support_files(self):
        provider_tech = self.invoice_id._get_active_tech_provider()
        files_size_max = provider_tech.maximum_megabytes * 1048576
        files_size = 0
        if len(self.attachment_ids) > provider_tech.num_doc_attachs:
            raise ValidationError(
                _(
                    'The maximum allowed number of files is: %s'
                    % (provider_tech.num_doc_attachs)
                )
            )
        for attach in self.attachment_ids:
            files_size += attach.file_size
            if files_size > files_size_max:
                raise ValidationError(
                    _(
                        'The maximum allowed file weight is: %s MB'
                        '\nPlease compress the file or remove some'
                        % (provider_tech.maximum_megabytes)
                    )
                )
        notes = self.line_ids.filtered(
            lambda line: line.method_type == 'note')
        elems = ['%s %s' % (line.code, line.value) for line in notes]
        extras = self.line_ids.filtered(
            lambda line: line.method_type != 'note')
        extra_refs = False
        if len(extras) > 0:
            elems2 = [{
                'parent_id': self.invoice_id.id,
                'custom_field_id': line.custom_field_id.id,
                'value': line.value} for line in extras]
            extra_refs = self.create_account_extra_ref(elems2)
        note = ' '.join(elems)
        self.invoice_id._action_post_files(
            self.attachment_ids, self.reconcile_line_ids, note, extra_refs)
