from datetime import datetime, timedelta, date
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestAccountPayment(TransactionCase):

    def setUp(self):
        super(TestAccountPayment, self).setUp()
        self.AccountJournal = self.env['account.journal']
        self.AccountAccount = self.env['account.account']
        self.ResBank = self.env['res.bank']
        self.Respartner = self.env['res.partner']
        self.ResPartnerBank = self.env['res.partner.bank']
        self.AccountPayment = self.env['account.payment']
        self.PaymentSupplier = self.env['account.collective.payments.supplier']
        self.FlatFileBase = self.env['account.flat.file.base']
        self.ResCompany = self.env['res.company'].search([])

        self.account_bank = self.AccountAccount.create({
            'code': "10151206",
            'name': "TEST Account Bank",
            'user_type_id': self.env.ref(
                'account.data_account_type_liquidity').id
        })
        self.account_payable = self.AccountAccount.create({
            'code': "23151206",
            'name': "TEST Account Payable",
            'user_type_id': self.env.ref(
                'account.data_account_type_payable').id,
            'reconcile': True
        })
        self.account_receivable = self.AccountAccount.create({
            'code': "21151206",
            'name': "TEST Account Payable",
            'user_type_id': self.env.ref(
                'account.data_account_type_receivable').id,
            'reconcile': True
        })
        self.res_partner = self.Respartner.create({
            'name': "Test Partner",
            'property_account_payable_id': self.account_payable.id,
            'property_account_receivable_id': self.account_receivable.id
        })
        self.res_bank = self.ResBank.create({
            'name': "Test Res Bank",
            'bic': "5"
        })
        self.res_partner_bank = self.ResPartnerBank.create({
            'bank_id': self.res_bank.id,
            'partner_id': self.ResCompany.partner_id.id,
            'acc_number': "159753456"
        })
        self.journal_bank = self.env['account.journal'].create({
            "name": "Test Bank",
            "code": "TESB",
            "type": "bank",
            'default_credit_account_id': self.account_bank.id,
            'default_debit_account_id':  self.account_bank.id,
            'bank_account_id': self.res_partner_bank.id
        })
        self.account_payment = self.AccountPayment.create({
            'journal_id': self.journal_bank.id,
            'payment_type': "outbound",
            'partner_type': "supplier",
            'amount': 2000,
            'payment_date': date(2020, 5, 30),
            'partner_id': self.res_partner.id,
            'payment_method_id': self.env.ref(
                'account.account_payment_method_manual_out').id
        })
        self.payment_supplier = self.PaymentSupplier.create({
            'journal_id': self.journal_bank.id,
            'payment_type': "outbound",
            'amount': 2000,
            'payment_date': date(2020, 5, 30),
            'company_id': self.ResCompany.id
        })

    def test_get_account_collective_payments_supplier(self):
        self.payment_supplier.generate_flat_file()

    def test_get_payment_context_flat_file(self):
        self.account_payment.generate_flat_file()

    def test_compute_acc_type(self):
        self.res_partner_bank._compute_acc_type()

    def test_export_flat_file(self):
        self.flat_file_base = self.FlatFileBase.create({
            'partner_id': self.account_payment.partner_id.id,
            'bank_id': (
                self.account_payment.journal_id.bank_account_id.bank_id.id),
            'account_debit': (
                self.account_payment.journal_id.bank_account_id.acc_number),
            'account_type': (
                self.account_payment.journal_id.bank_account_id.acc_type),
            'file_extension': "txt",
            'file_type': "get_collect_data_bank"
        })
        self.flat_file_base.with_context(
            payment_name=self.account_payment.name).export_flat_file()
