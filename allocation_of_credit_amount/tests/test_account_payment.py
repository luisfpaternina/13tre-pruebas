# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

import datetime


class TestPayment(TransactionCase):

    def setUp(self):
        super(TestPayment, self).setUp()
        self.credit_class = self.env['credit']
        self.res_partner_id = self.env['res.partner'].search([])[0]
        self.res_bank_id = self.env['res.bank'].search([])[0]
        self.credit_type_id = self.env['credit.type'].create({
            'name': 'Credit Type Test',
            'code': 'ASJ23',
            'description': 'Credit type for credits',
            'supporting_entity_ids': [(6, 0, [self.res_bank_id.id, ])]
        })
        self.payment_class = self.env['account.payment']
        self.move_class = self.env['account.move']
        self.move_line_class = self.env['account.move.line']
        self.account_class = self.env['account.account']
        self.account_type_class = self.env['account.account.type']
        self.journal_class = self.env['account.journal']
        self.payment_method_class = self.env['account.payment.method']

        # Records #

        self.account_id = self.account_class.create({
            'code': '12345',
            'name': 'Test Account',
            'user_type_id': self.env.ref('account.data_account_type_liquidity').id,
            'company_id': 1,
            'currency_id': self.env.company.currency_id.id,
        })

        self.journal_id = self.env.ref(
            'allocation_of_credit_amount.payment_of_credits_dairy'
        )

        self.payment_method_id = self.payment_method_class.create({
            'name': "Payment Method Test",
            'code': 'PMT',
            'payment_type': 'inbound',
        })

    def test_payment_post_nomove_context(self):

        self.res_partner_id.write({
            'property_account_receivable_id': self.account_id.id,
        })

        self.journal_id.write({
            'default_debit_account_id': self.account_id.id,
            'default_credit_account_id': self.account_id.id,
        })

        debit_move_line_vals = {
            'account_id': self.account_id.id,
            'debit': 10000,
            'credit': 0,
            'display_type': False,
        }

        credit_move_line_vals = {
            'account_id': self.account_id.id,
            'debit': 0,
            'credit': 10000,
            'display_type': False,
        }

        self.move_id = self.move_class.with_context(
            {
                'default_currency_id': 1,
                'default_journal_id': self.journal_id.id,
                'default_type': 'out_invoice',
            }
        ).create({
            'type': 'out_invoice',
            'line_ids': [
                (0, 0, debit_move_line_vals), (0, 0, credit_move_line_vals)
            ]
        })

        payment_vals = {
            'payment_type': 'inbound', 
            'partner_type': 'customer', 
            'partner_id': self.res_partner_id.id, 
            'amount': 10000, 
            'currency_id': self.env.company.currency_id.id, 
            'payment_date': '2021-10-14', 
            'communication': self.move_id.name, 
            'payment_difference_handling': 'open', 
            'writeoff_label': 'Write-Off', 
            'journal_id': self.journal_id.id, 
            'destination_journal_id': False, 
            'payment_method_id': self.payment_method_id.id, 
            'payment_token_id': False, 
            'partner_bank_account_id': False, 
            'check_amount_in_words': 'Diez Mil Pesos', 
            'writeoff_account_id': False, 
            'message_attachment_count': 0,
        }

        self.payment_id = self.payment_class.create(payment_vals)

        self.payment_id.with_context(
            {
                'active_model': 'payment_test',
                'active_ids': [],
            }
        ).post()

    def test_payment_post(self):

        self.res_partner_id.write({
            'property_account_receivable_id': self.account_id.id,
        })

        self.journal_id.write({
            'default_debit_account_id': self.account_id.id,
            'default_credit_account_id': self.account_id.id,
        })

        credit_id = self.credit_class.create({
            'res_partner_id': self.res_partner_id.id,
            'credit_type_id': self.credit_type_id.id,
            'number_credit': 1,
            'modality': 'amortized',
            'credit_limit': 2000000,
            'sponsoring_entity_id': self.res_bank_id.id,
            'endorsement_commission': 1,
            'disbursement_date': datetime.date(2021, 9, 7),
            'term_months': 4,
            'credit_value_accounted':2002000,
        })

        credit_id.calculate_payment_schedule()
        credit_id.publish_receipts()

        line_counter = 0
        for line in credit_id.credit_lines:
            receipt = line.receipt_id
            if line_counter == 1:
                line.receipt_id = False
            elif line_counter == 2:
                line_validate = True
            payment_vals = {
                'payment_type': 'inbound', 
                'partner_type': 'customer', 
                'partner_id': receipt.partner_id.id, 
                'amount': receipt.amount_total, 
                'currency_id': self.env.company.currency_id.id, 
                'payment_date': '2021-10-14', 
                'communication': receipt.name, 
                'payment_difference_handling': 'open', 
                'writeoff_label': 'Write-Off', 
                'journal_id': receipt.journal_id.id, 
                'payment_method_id': self.payment_method_id.id, 
            }

            payment_id = self.payment_class.create(payment_vals)

            payment_id.with_context(
                {
                    'active_model': 'account.move',
                    'active_ids': [receipt.id],
                }
            ).post()

            if line_counter == 1:
                receipt.amount_residual = 100
                line.receipt_id = receipt.id
            line_counter += 1

        credit_revolving_id = self.credit_class.create({
            'res_partner_id': self.res_partner_id.id,
            'credit_type_id': self.credit_type_id.id,
            'number_credit': 1,
            'modality': 'revolving',
            'credit_limit': 2000000,
            'sponsoring_entity_id': self.res_bank_id.id,
            'endorsement_commission': 1,
            'disbursement_date': datetime.date(2021, 9, 7),
            'term_months': 4,
            'credit_value_accounted':2002000,
        })

        credit_revolving_id.calculate_payment_schedule()
        credit_revolving_id.publish_receipts()

        line_counter = 0
        for line in credit_revolving_id.credit_lines:
            receipt = line.receipt_id
            if line_counter == 1:
                line.receipt_id = False
            elif line_counter == 2:
                line_validate = True
            elif line_counter == 3:
                line.capital_subscription = 2000010
            payment_vals = {
                'payment_type': 'inbound', 
                'partner_type': 'customer', 
                'partner_id': receipt.partner_id.id, 
                'amount': receipt.amount_total, 
                'currency_id': self.env.company.currency_id.id, 
                'payment_date': '2021-10-14', 
                'communication': receipt.name, 
                'payment_difference_handling': 'open', 
                'writeoff_label': 'Write-Off', 
                'journal_id': receipt.journal_id.id, 
                'payment_method_id': self.payment_method_id.id, 
            }

            payment_id = self.payment_class.create(payment_vals)

            payment_id.with_context(
                {
                    'active_model': 'account.move',
                    'active_ids': [receipt.id],
                }
            ).post()

            if line_counter == 1:
                receipt.amount_residual = 100
                line.receipt_id = receipt.id
            line_counter += 1