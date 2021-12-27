from datetime import datetime, date, timedelta
from odoo.fields import Date
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestAccountMovePartnerIva(TransactionCase):

    def setUp(self):
        super(TestAccountMovePartnerIva, self).setUp()
        self.account_account = self.env['account.account']
        self.account_journal = self.env['account.journal']
        self.account_move = self.env['account.move']
        self.res_partner = self.env['res.partner']
        self.res_company = self.env['res.company']
        self.company = self.env.ref('base.main_company')
        self.company.country_id = self.env.ref('base.co')
        self.company.template_code = '01'

        self.res_partner = self.env['res.partner'].create({
            'name': "TST Partner",
        })
        self.res_partner_2 = self.env['res.partner'].create({
            'name': "TST2 Partner",
        })

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
        self.journal = self.account_journal.create({
            'name': 'Test Journal',
            'type': 'general',
            'code': 'TSTJ1',
            'company_id': self.company.id
        })
        self.account_1 = self.account_account.create({
            'name': 'Test Account 1',
            'code': '51236877',
            'user_type_id': self.env.ref(
                'account.data_account_type_current_assets').id,
            'company_id': self.company.id
        })
        self.account_2 = self.account_account.create({
            'name': 'Test Account 2',
            'code': '51236883',
            'user_type_id': self.env.ref(
                'account.data_account_type_current_assets').id,
            'company_id': self.company.id
        })
        self.tax_group_1 = self.env['account.tax.group'].create(
            {'name': 'IVA'})
        self.tax_group_2 = self.env['account.tax.group'].create(
            {'name': 'ReteFuente'})

        self.tax = self.env['account.tax'].create({
            'name': 'Tax 19%',
            'amount': 19,
            'type_tax_use': 'sale',
            'tax_group_id': self.tax_group_1.id
        })

        self.retention_tax = self.env['account.tax'].create({
            'name': 'TEST: RteFte -3.50% Ventas',
            'amount': -3.50,
            'type_tax_use': 'sale',
            'tax_group_id': self.tax_group_2.id
        })

        self.retention_tax2 = self.env['account.tax'].create({
            'name': 'TEST: RteIVA 15% sobre el 19% IVA Ventas%',
            'amount': -15,
            'type_tax_use': 'sale',
            'tax_group_id': self.tax_group_2.id
        })
        self.tax_lines = [
            self.tax.id,
            self.retention_tax.id,
            self.retention_tax2.id
        ]

    def test_onchange_mark_recompute_taxes(self):
        move_1 = self.account_move.new({
            'journal_id': self.journal.id,
            'date': date(2021, 3, 9),
            'company_id': self.company.id,
            'line_ids': [(0, 0, {
                'account_id': self.account_1.id,
                'partner_id': self.res_partner.id,
                'journal_id': self.journal.id,
                'credit': 0.0,
                'debit': 1000.0,
                "tax_ids": [(6, 0, self.tax_lines)]
            }), (0, 0, {
                'account_id': self.account_2.id,
                'partner_id': self.res_partner.id,
                'journal_id': self.journal.id,
                'credit': 1000.0,
                'debit': 0.0
            })]
        })
        move_1.line_ids[0]._onchange_mark_recompute_taxes()

    def test_recompute_tax_lines(self):
        move_1 = self.account_move.new({
            'journal_id': self.journal.id,
            'date': date(2021, 3, 9),
            'company_id': self.company.id,
            'line_ids': [(0, 0, {
                'account_id': self.account_1.id,
                'partner_id': self.res_partner.id,
                'journal_id': self.journal.id,
                'credit': 0.0,
                'debit': 1000.0,
                "tax_ids": [(6, 0, self.tax_lines)],
            }), (0, 0, {
                'account_id': self.account_2.id,
                'partner_id': self.res_partner.id,
                'journal_id': self.journal.id,
                'credit': 1190.0,
                'debit': 0.0,
            })]
        })
        move_1._compute_invoice_taxes_by_group()
        move_1._recompute_tax_lines(True)
        move_1.line_ids[0].update({
            'partner_id': self.res_partner_2.id,
        })
        move_1._compute_invoice_taxes_by_group()
        move_1._recompute_tax_lines(True)

    def test_delete_tax_lines(self):
        move_1 = self.account_move.new({
            'journal_id': self.journal.id,
            'date': date(2021, 3, 9),
            'company_id': self.company.id,
            'line_ids': [(0, 0, {
                'account_id': self.account_1.id,
                'partner_id': self.res_partner.id,
                'journal_id': self.journal.id,
                'credit': 0.0,
                'debit': 1000.0,
                "tax_ids": [(6, 0, self.tax_lines)],
            }), (0, 0, {
                'account_id': self.account_2.id,
                'partner_id': self.res_partner.id,
                'journal_id': self.journal.id,
                'credit': 1190.0,
                'debit': 0.0,
            })]
        })
        move_1._recompute_taxes_on_delete()
