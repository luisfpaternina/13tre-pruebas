# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

import datetime
from datetime import timedelta


class TestCredit(TransactionCase):

    def setUp(self):
        super(TestCredit, self).setUp()
        self.credit = self.env['credit']
        self.res_partner_id = self.env['res.partner'].search([])[0]
        self.res_bank_id = self.env['res.bank'].search([])[0]
        self.credit_type_id = self.env['credit.type'].create({
            'name': 'Credit Type Test',
            'code': 'ASJ23',
            'description': 'Credit type for credits',
            'supporting_entity_ids': [(6, 0, [self.res_bank_id.id, ])]
        })
        self.account_class = self.env['account.account']
        self.account_id = self.account_class.create({
            'code': '12345',
            'name': 'Test Account',
            'user_type_id': self.env.ref('account.data_account_type_liquidity').id,
            'company_id': 1,
            'currency_id': self.env.company.currency_id.id,
        })
        self.res_partner_id.write({
            'property_account_receivable_id': self.account_id.id,
        })
        self.journal_id = self.env.ref(
            'allocation_of_credit_amount.payment_of_credits_dairy'
        )
        self.journal_id.write({
            'default_debit_account_id': self.account_id.id,
            'default_credit_account_id': self.account_id.id,
        })

    def test_asign_name(self):
        credit_id = self.credit.create({
            'res_partner_id': self.res_partner_id.id,
            'credit_type_id': self.credit_type_id.id,
            'number_credit': 0,
            'modality': 'revolving',
            'credit_limit': 2000000,
            'sponsoring_entity_id': self.res_bank_id.id
        })
        credit_id.asign_name()
        credit_id.update({
            'number_credit': 884938
        })
        credit_id.asign_name()
        credit_id.update({
            'res_partner_id': False
        })
        credit_id.asign_name()
        self.assertTrue(
            credit_id.name == (
                f'{self.res_partner_id.name} - ' +
                f'{int(credit_id.number_credit)}'
            )
        )
        credit_id._onchange_credit_type_id()

    def test_calculate_endorsement_value_plus_vat_and_value_accounted(self):
        credit_id = self.credit.create({
            'res_partner_id': self.res_partner_id.id,
            'credit_type_id': self.credit_type_id.id,
            'number_credit': 0,
            'modality': 'revolving',
            'credit_limit': 2000000,
            'sponsoring_entity_id': self.res_bank_id.id,
            'endorsement_commission': 5,
            'credit_limit': 1000000,
            'disbursement_date': datetime.date(2021, 9, 27),
            'term_months': 12,
        })
        credit_id._calculate_endorsement_value_plus_vat()
        self.assertTrue(credit_id.endorsement_value_plus_vat == 59500)
        credit_id._calculate_credit_value_accounted()
        self.assertTrue(credit_id.credit_value_accounted == 1059500)

    def test_calculate_payment_schedule(self):
        credit_id = self.credit.create({
            'res_partner_id': self.res_partner_id.id,
            'credit_type_id': self.credit_type_id.id,
            'number_credit': 0,
            'modality': 'revolving',
            'credit_limit': 2000000,
            'sponsoring_entity_id': self.res_bank_id.id,
            'endorsement_commission': 5,
            'credit_limit': 1000000,
            'disbursement_date': datetime.date(2021, 9, 27),
            'term_months': 12,
        })
        credit_id._calculate_endorsement_value_plus_vat()
        credit_id._calculate_credit_value_accounted()
        credit_id.calculate_payment_schedule()

    def test_validation_error_payment(self):
        credit_id = self.credit.create({
            'res_partner_id': self.res_partner_id.id,
            'credit_type_id': self.credit_type_id.id,
            'number_credit': 0,
            'modality': 'revolving',
            'credit_limit': 2000000,
            'sponsoring_entity_id': self.res_bank_id.id,
            'endorsement_commission': 5,
            'credit_limit': 1000000,
            'disbursement_date': datetime.date(2021, 9, 27)
        })
        credit_id._calculate_endorsement_value_plus_vat()
        credit_id._calculate_credit_value_accounted()
        with self.assertRaises(ValidationError):
            credit_id.calculate_payment_schedule()

    def test_asign_name_credit_lines(self):
        credit_id = self.credit.create({
            'res_partner_id': self.res_partner_id.id,
            'credit_type_id': self.credit_type_id.id,
            'number_credit': 0,
            'modality': 'revolving',
            'credit_limit': 2000000,
            'sponsoring_entity_id': self.res_bank_id.id,
            'endorsement_commission': 5,
            'credit_limit': 1000000,
            'disbursement_date': datetime.date(2021, 9, 27),
            'term_months': 12,
        })
        credit_id._calculate_endorsement_value_plus_vat()
        credit_id._calculate_credit_value_accounted()
        credit_id.calculate_payment_schedule()
        credit_lines = self.env['credit.line'].search([])
        credit_lines[0].update({
            'installment_number': False
        })
        credit_lines._asign_name()

    def test_change_invoice_number(self):

        credit_id = self.credit.create({
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

        credit_id.calculate_payment_schedule()

        line_validation = True
        for line in credit_id.credit_lines:
            if line_validation:
                line.receipt_id = False
                line_validation = False
            else:
                line_validation = True

        credit_id.publish_receipts()
        credit_id._update_receipts_notes()

        credit_with_invoice_id = self.credit.create({
            'res_partner_id': self.res_partner_id.id,
            'credit_type_id': self.credit_type_id.id,
            'invoice_number': '41967436',
            'number_credit': 1,
            'modality': 'revolving',
            'credit_limit': 2000000,
            'sponsoring_entity_id': self.res_bank_id.id,
            'endorsement_commission': 1,
            'disbursement_date': datetime.date(2021, 9, 7),
            'term_months': 4,
            'credit_value_accounted':2002000,
        })

        credit_with_invoice_id.calculate_payment_schedule()
        credit_with_invoice_id.publish_receipts()
        credit_with_invoice_id._update_receipts_notes()

    def test_check_status_credit(self):

        check_credit_id = self.credit.create({
            'res_partner_id': self.res_partner_id.id,
            'credit_type_id': self.credit_type_id.id,
            'invoice_number': '41967436',
            'number_credit': 1,
            'modality': 'revolving',
            'credit_limit': 2000000,
            'sponsoring_entity_id': self.res_bank_id.id,
            'endorsement_commission': 1,
            'disbursement_date': datetime.date(2021, 9, 7),
            'term_months': 4,
            'credit_value_accounted':2002000,
            'state': 'active',
        })

        check_credit_id.calculate_payment_schedule()

        line_counter = 0
        for line in check_credit_id.credit_lines:
            receipt = line.receipt_id
            if line_counter == 1:
                line.receipt_id = False
            elif line_counter == 2:
                receipt.amount_residual = 50000
                receipt.write({
                    'invoice_date_due': datetime.date.today() - timedelta(days=3),
                })
            elif line_counter == 3:
                receipt.amount_residual = 150000
            line_counter += 1

        check_credit_id.check_credit_line_status()

        check_credit_paid_id = self.credit.create({
            'res_partner_id': self.res_partner_id.id,
            'credit_type_id': self.credit_type_id.id,
            'invoice_number': '41967436',
            'number_credit': 1,
            'modality': 'revolving',
            'credit_limit': 2000000,
            'sponsoring_entity_id': self.res_bank_id.id,
            'endorsement_commission': 1,
            'disbursement_date': datetime.date(2021, 9, 7),
            'term_months': 4,
            'credit_value_accounted':2002000,
            'state': 'active',
        })
        check_credit_paid_id.calculate_payment_schedule()

        for line in check_credit_paid_id.credit_lines:
            line.receipt_id.amount_residual = 0

        check_credit_paid_id.check_credit_line_status()

        check_credit_due_date_id = self.credit.create({
            'res_partner_id': self.res_partner_id.id,
            'credit_type_id': self.credit_type_id.id,
            'invoice_number': '41967436',
            'number_credit': 1,
            'modality': 'revolving',
            'credit_limit': 2000000,
            'sponsoring_entity_id': self.res_bank_id.id,
            'endorsement_commission': 1,
            'disbursement_date': datetime.date(2021, 9, 7),
            'term_months': 4,
            'credit_value_accounted':2002000,
            'state': 'active',
        })
        check_credit_due_date_id.calculate_payment_schedule()

        for line in check_credit_due_date_id.credit_lines:
            receipt = line.receipt_id
            receipt.amount_residual = 50000
            receipt.write({
                'invoice_date_due': datetime.date.today() + timedelta(days=3),
            })

        check_credit_due_date_id.check_credit_line_status()

    def test_unlink_receipts(self):

        credit_ok_id = self.credit.create({
            'res_partner_id': self.res_partner_id.id,
            'credit_type_id': self.credit_type_id.id,
            'invoice_number': '41967436',
            'number_credit': 1,
            'modality': 'revolving',
            'credit_limit': 2000000,
            'sponsoring_entity_id': self.res_bank_id.id,
            'endorsement_commission': 1,
            'disbursement_date': datetime.date(2021, 9, 7),
            'term_months': 4,
            'credit_value_accounted':2002000,
            'state': 'active',
        })
        credit_ok_id.calculate_payment_schedule()
        credit_ok_id.unlink()

        try:
            credit_wrong_id = self.credit.create({
                'res_partner_id': self.res_partner_id.id,
                'credit_type_id': self.credit_type_id.id,
                'invoice_number': '41967436',
                'number_credit': 1,
                'modality': 'revolving',
                'credit_limit': 2000000,
                'sponsoring_entity_id': self.res_bank_id.id,
                'endorsement_commission': 1,
                'disbursement_date': datetime.date(2021, 9, 7),
                'term_months': 4,
                'credit_value_accounted':2002000,
                'state': 'active',
            })
            credit_wrong_id.calculate_payment_schedule()
            credit_wrong_id.publish_receipts()

            credit_wrong_id.unlink()
        except:
            pass

        credit_lines_ok_id = self.credit.create({
            'res_partner_id': self.res_partner_id.id,
            'credit_type_id': self.credit_type_id.id,
            'invoice_number': '41967436',
            'number_credit': 1,
            'modality': 'revolving',
            'credit_limit': 2000000,
            'sponsoring_entity_id': self.res_bank_id.id,
            'endorsement_commission': 1,
            'disbursement_date': datetime.date(2021, 9, 7),
            'term_months': 4,
            'credit_value_accounted':2002000,
            'state': 'active',
        })
        credit_lines_ok_id.calculate_payment_schedule()
        for line in credit_lines_ok_id.credit_lines:
            line.unlink()
