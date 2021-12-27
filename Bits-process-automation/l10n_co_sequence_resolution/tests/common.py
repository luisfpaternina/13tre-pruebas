from datetime import datetime, timedelta
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo.fields import Date


class TestSequenceResolutionBase(TransactionCase):

    def setUp(self):
        super(TestSequenceResolutionBase, self).setUp()
        self.dian_resolution = {
            'sequence_id': False,
            'resolution_number': 1,
            'date_from': datetime.now(),
            'date_to': datetime.now()+timedelta(days=365),
            'number_from': 1,
            'number_to': 100,
            'active_resolution': True,
        }
        self.ir_sequence = self.env['ir.sequence'].create({
            'name': 'Facturacion Electronica',
            'use_dian_control': True,
            'dian_type': 'computer_generated_invoice',
            'date_range_ids': [[
                0,
                0,
                self.dian_resolution
            ]]
        })
        self.company = self.env.ref('base.main_company')
        self.company.country_id = self.env.ref('base.co')

        self.account_type_sale = self.env['account.account.type'].create({
            'name': 'income',
            'type': 'other',
            'internal_group': 'income',
        })
        self.account_sale = self.env['account.account'].create({
            'name': 'Product Sales ',
            'code': 'S200000',
            'user_type_id': self.account_type_sale.id,
            'company_id': self.company.id,
            'reconcile': False
        })
        self.sale_journal = self.env['account.journal'].create({
            'name': 'reflets.info',
            'code': 'ref',
            'type': 'sale',
            'company_id': self.company.id,
            'sequence_id': self.env['ir.sequence'].search([], limit=1).id,
            'default_credit_account_id': self.account_sale.id,
            'default_debit_account_id': self.account_sale.id
        })
        self.salesperson = self.env.ref('base.user_admin')
        self.salesperson.function = 'Sales'
        self.invoice_dicc = {
            'type': 'out_invoice',
            'invoice_user_id': self.salesperson.id,
            'name': 'OC 123',
            'journal_id': self.sale_journal.id,
            'currency_id': self.company.currency_id.id,
        }
