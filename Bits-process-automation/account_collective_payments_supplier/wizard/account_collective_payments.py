# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountCollectivePayments(models.TransientModel):
    _inherit = 'account.collective.payments.wizard'

    supplier_payment = fields.Boolean(
        string=_("Supplier Payment")
    )

    @api.onchange(
        'date_from_f',
        'date_to_f',
        'journal_id_f',
        'account_id_f',
        'partner_id_f',
        'bank_id',
        'supplier_payment')
    def _onchange_line_list(self):
        domain = super(AccountCollectivePayments, self)._onchange_line_list()
        if self.supplier_payment:
            domain["domain"]["line_ids"] += [
                ('journal_id.type', '=', 'purchase'),
                ('account_id.internal_type', '=', 'payable'),
                ('move_id.type', 'in', [
                    'in_invoice', 'in_refund', 'in_receipt'])
            ]
        return domain

    def generate_payments_action(self):
        payment = self.env['account.payment']
        payment_supplier = self.env['account.collective.payments.supplier']
        for record in self:
            if record.supplier_payment:
                payment_supplier_vals = record._get_payment_supplier_vals()
                payment_supplier_id = payment_supplier.create(
                    payment_supplier_vals)

                payments = record._create_payment_groups(record.line_ids)
                record._register_payments(payments, payment_supplier_id.id)

                return {
                    'name': _('Payment to Suppliers'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'account.collective.payments.supplier',
                    'res_id': payment_supplier_id.id,
                }
            else:
                payment_vals = record._get_collective_payment_vals()
                payment_id = payment.create(payment_vals)
                self._generate_journal_entry(payment_id)

                record.reconcile_process(payment_id)
                payment_id.state = 'posted'

                return {
                    'name': _('Payment'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'account.payment',
                    'domain': [('id', 'in', [payment_id.id])]
                }

    def _get_payment_supplier_vals(self):
        values = {
            'name': _('Collective Payment (') + str(self.payment_date) + ")",
            'journal_id': self.journal_id.id,
            'payment_method_dian_id': self.payment_method_dian_id.id,
            'payment_way_dian_id': self.payment_way_dian_id.id,
            'payment_date': self.payment_date,
            'payment_type': self.payment_type,
            'amount': abs(self.amount),
            'currency_id': self.company_id.currency_id.id,
            'company_id': self.company_id.id
        }
        return values

    def _get_payment_register_vals(self, data):
        payment_method = self.env['account.payment.method'].search([
            ("code", "=", "electronic_out")
        ])
        values = {
            'payment_date': self.payment_date,
            'journal_id': self.journal_id.id,
            'payment_method_id': payment_method.id,
            'invoice_ids': data.get("bills", []),
            'group_payment': True
        }
        return values

    def _create_payment_groups(self, line_ids):
        payments = dict()
        for move_line in line_ids:
            parter_id = move_line.partner_id.id
            account_id = move_line.account_id.id
            key = str(str(parter_id) + "_" + str(account_id))

            if not payments.get(key, False):
                payments[key] = dict()
                payments[key]["bills"] = []
                payments[key]["amount"] = 0

            payments[key]["bills"].append(move_line.move_id.id)
            payments[key]["amount"] += move_line.credit

        return payments

    def _register_payments(self, payments, payment_supplier_id):
        payment_register = self.env['account.payment.register']
        for payment in payments.values():
            vals = self._get_payment_register_vals(payment)
            register_payment = payment_register.create(vals)
            self._create_payments(register_payment, payment_supplier_id)

    def _create_payments(self, register_payment, payment_supplier_id):
        account_payment = self.env['account.payment']
        payment_vals = register_payment.get_payments_vals()
        payments = account_payment.create(payment_vals)
        for payment in payments:
            payment.write({
                "account_collective_payments_supplier_id": payment_supplier_id
                })
        payments.post()
