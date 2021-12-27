import odoo.tests

from datetime import date
from datetime import datetime, timedelta

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo import fields, models, tools


class TestAccountFlatFileDavivienda(TransactionCase):

    def setUp(self):
        super(TestAccountFlatFileDavivienda, self).setUp()
        self.AccountJournal = self.env['account.journal']
        self.AccountAccount = self.env['account.account']
        self.ResBank = self.env['res.bank']
        self.Respartner = self.env['res.partner']
        self.ResPartnerBank = self.env['res.partner.bank']
        self.AccountPayment = self.env['account.payment']
        self.FlatFile = self.env['account.flat.file.base']
        self.PaymentSupplier = self.env['account.collective.payments.supplier']
        self.ResCompany = self.env['res.company'].search([])
        self.wizard_payment = self.env['account.collective.payments.wizard']
        self.ResCompany = self.env['res.company'].browse([1])

        self.partner_company = self.ResCompany.partner_id
        self.partner_company.write({
            'document_type': '31',
            'number_identification': '753159456-8'
        })

        self.ir_sequence = self.env['ir.sequence'].create({
            'name': 'SEQ',
            'padding': 4,
            'number_increment': 1,
        })

        self.account_journal = self.AccountJournal.create({
            'name': 'MISC',
            'code': 'MSC',
            'type': 'general',
            'sequence_id': self.ir_sequence.id,
        })

        self.account_bank = self.AccountAccount.create({
            'code': "10151206",
            'name': "TEST Account Bank",
            # 'create_asset': 'validate',
            'user_type_id': self.env.ref(
                'account.data_account_type_liquidity').id
        })
        self.account_payable = self.AccountAccount.create({
            'code': "23151206",
            'name': "TEST Account Payable",
            # 'create_asset': 'validate',
            'user_type_id': self.env.ref(
                'account.data_account_type_payable').id,
            'reconcile': True
        })
        self.account_receivable = self.AccountAccount.create({
            'code': "21151206",
            'name': "TEST Account Payable",
            # 'create_asset': 'validate',
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
            'bic': "51"
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
            'partner_id': self.partner_company.id,
            'payment_method_id': self.env.ref(
                'account.account_payment_method_manual_out').id
        })

        self.hr_contract = self.env['hr.contract']
        self.hr_payslip = self.env['hr.payslip']
        self.hr_employee = self.env['hr.employee']
        self.hr_salary_rule = self.env['hr.salary.rule']
        self.hr_salary_rule_category = self.env['hr.salary.rule.category']
        self.hr_payroll_structure = self.env['hr.payroll.structure']
        self.hr_payroll_structure_type = self.env['hr.payroll.structure.type']

        self.payable_type_id = self.env.ref(
            'account.data_account_type_payable')

        self.salary_rule_category = self.hr_salary_rule_category.create({
            'name': "Salary Category Test",
            'code': "SCT"
        })

        self.structure_type = self.hr_payroll_structure_type.create({
            'name': "Test Type",
            'wage_type': "monthly"
        })

        self.contract = self.hr_contract.create({
            'name': "Contract Test",
            'date_start': datetime.now(),
            'date_end': datetime.now()+timedelta(days=365),
            'wage': 3150000,
            'structure_type_id': self.structure_type.id
        })

        self.employee = self.hr_employee.create({
            'name': "Test Payroll News",
            'contract_id': self.contract.id,
            'document_type': '13',
            'identification_id': "75395146",
            'names': 'NOMBRE1 NOMBRE2',
            'surnames': 'APELLIDO1 APELLIDO2',
            'known_as': 'SuperCode',
        })

        self.payroll_structure = self.hr_payroll_structure.create({
            'name': "Structure Test",
            'type_id': self.structure_type.id,
            # 'journal_id': self.account_journal.id,
        })

        self.salary_rule = self.hr_salary_rule.create({
            'name': "ITEM PARAFISCAL",
            'code': "001",
            'sequence': 100,
            'struct_id': self.payroll_structure.id,
            'category_id': self.salary_rule_category.id,
            'condition_select': "none",
            'amount_select': "fix",
            'amount_fix': 3000,
            'quantity': 1.0,
            # "account_debit": self.account_payable.id,
            # "account_credit": self.account_payable.id,
        })

        self.payslip = self.hr_payslip.create({
            'name': "Payroll Test",
            'employee_id': self.employee.id,
            'contract_id': self.contract.id,
            # 'journal_id': self.account_journal.id,
            'struct_id': self.payroll_structure.id,
            # 'general_state': 'approved',
            'date_from': datetime.now(),
            'date_to': datetime.now()+timedelta(days=365)
        })

    def test_without_active_model_get_collect_data(self):
        self.account_payment.post()
        record = self.FlatFile.new({
            'partner_id': self.account_payment.partner_id.id,
            'payment_description': "DEMO001",
            'transaction_type': 'electronic_transaction',
            'application_date': '2020-05-01',
            'file_type': 'get_collect_data_bank',
            'bank_id': self.res_bank
        })
        ctx = {
            'payment_name': self.account_payment.name,
            'payment_type': 'Payment',
            'active_model': 'account.payment',
            'active_id': self.account_payment.id,
        }
        res = record.with_context(ctx).get_collect_data_bank()

    def test_get_nit_company(self):
        self.account_payment.post()
        record = self.FlatFile.new({
            'partner_id': self.account_payment.partner_id.id,
            'payment_description': "DEMO001",
            'transaction_type': 'electronic_transaction',
            'application_date': '2020-05-01',
            'file_type': 'get_collect_data_bank',
            'bank_id': self.res_bank
        })
        res = record.get_nit_company(16, {})

    def test_get_company_document_type(self):
        self.account_payment.post()
        record = self.FlatFile.new({
            'partner_id': self.account_payment.partner_id.id,
            'payment_description': "DEMO001",
            'transaction_type': 'electronic_transaction',
            'application_date': '2020-05-01',
            'file_type': 'get_collect_data_bank',
            'bank_id': self.res_bank
        })
        res = record.get_company_document_type(2, {})

    def test_validate_bank(self):
        self.account_payment.post()
        self.res_bank.write({
            'bic': '1'
        })
        record = self.FlatFile.new({
            'partner_id': self.account_payment.partner_id.id,
            'payment_description': "DEMO001",
            'transaction_type': 'electronic_transaction',
            'application_date': '2020-05-01',
            'file_type': 'get_collect_data_bank',
            'bank_id': self.res_bank
        })
        res = record.get_collect_data_bank()

    def test_get_nit_company_not_verification_digit(self):
        self.partner_company.write({
            'number_identification': '753159456'
        })
        self.account_payment.post()
        record = self.FlatFile.new({
            'partner_id': self.account_payment.partner_id.id,
            'payment_description': "DEMO001",
            'transaction_type': 'electronic_transaction',
            'application_date': '2020-05-01',
            'file_type': 'get_collect_data_bank',
            'bank_id': self.res_bank
        })
        res = record.get_nit_company(16, {})

    def test_get_number_identification_not_verification_digit(self):
        self.partner_company.write({
            'number_identification': '753159456'
        })
        self.account_payment.post()
        record = self.FlatFile.new({
            'partner_id': self.account_payment.partner_id.id,
            'payment_description': "DEMO001",
            'transaction_type': 'electronic_transaction',
            'application_date': '2020-05-01',
            'file_type': 'get_collect_data_bank',
            'bank_id': self.res_bank
        })
        res = record.with_context(
            active_id=self.account_payment.id,
            payment_type='Payment').get_collect_data_bank()

    def test_account_collective_payment_supplier(self):
        payment_supplier = self.PaymentSupplier.create({
            'company_id': self.ResCompany.id,
            'payment_date': '2020-05-01'
        })
        account_payment = self.AccountPayment.create({
            'journal_id': self.journal_bank.id,
            'payment_type': "outbound",
            'partner_type': "supplier",
            'amount': 2000.1,
            'payment_date': date(2020, 5, 30),
            'partner_id': self.partner_company.id,
            'payment_method_id': self.env.ref(
                'account.account_payment_method_manual_out').id,
            'account_collective_payments_supplier_id': payment_supplier.id
        })
        record = self.FlatFile.new({
            'partner_id': self.account_payment.partner_id.id,
            'payment_description': "DEMO001",
            'transaction_type': 'electronic_transaction',
            'application_date': '2020-05-01',
            'bank_id': self.res_bank
        })
        self.account_payment.post()
        res = record.with_context(
            active_id=payment_supplier.id,
            payment_type='Supplier').get_collect_data_bank()
