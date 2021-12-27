# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from odoo.fields import Date
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestFECommon(TransactionCase):

    def setUp(self):
        super(TestFECommon, self).setUp()
        self.tech_provider = self.env['l10n_co.tech.provider']
        self.ref_act_fields = self.env['account.act.fields']
        self.tech_provider_line = self.env['l10n_co.tech.provider.line']
        self.DianFiscalResp = self.env['dian.fiscal.responsability']
        self.DianFiscalRespLine = self.env['dian.fiscal.responsability.line']
        self.TaxType = self.env['account.tax.type']
        self.ref_code_desc = self.env['l10n_co.description_code']
        self.AccountPayment = self.env['account.payment']

        self.company = self.env.ref('base.main_company')
        self.company.country_id = self.env.ref('base.co')
        self.company.template_code = '01'
        self.company.header_regimen_activity = 'Regimen/Actividad'
        self.company.header_rate = 'Tasa de cobro'
        self.company.header_decree = 'Decreto'
        self.responsability = self.DianFiscalResp.search(
            [('code', '=', 'O-47')])
        self.company.partner_id.fiscal_responsibility = self.responsability.id

        self.partner = self.env['res.partner'].create({
            'name': "TST Partner",
            'fiscal_responsibility': self.responsability.id
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

        self.dian_resolution = {
            'sequence_id': False,
            'resolution_number': 1,
            'date_from': datetime.now(),
            'date_to': datetime.now()+timedelta(days=365),
            'number_from': 1,
            'number_to': 100,
            'active_resolution': True,
        }
        self.sequence_id = self.env['ir.sequence'].create({
            'name': 'Facturacion Electronica',
            'use_dian_control': True,
            'dian_type': 'computer_generated_invoice',
            'date_range_ids': [[
                0,
                0,
                self.dian_resolution
            ]]
        })

        self.sale_journal = self.env['account.journal'].create({
            'name': 'reflets.info',
            'code': 'ref',
            'type': 'sale',
            'company_id': self.company.id,
            'sequence_id': self.sequence_id.id,
            'default_credit_account_id': self.account_sale.id,
            'default_debit_account_id': self.account_sale.id
        })
        self.account = self.env['account.account'].create({
            'code': "111005",
            'name': "TST Account",
            'user_type_id': (
                self.env.ref('account.data_account_type_liquidity').id),
            'reconcile': True
        })
        self.tax_group_1 = self.env['account.tax.group'].create(
            {'name': 'IVA'})
        self.tax_group_2 = self.env['account.tax.group'].create(
            {'name': 'ReteFuente'})

        self.tax = self.env['account.tax'].create({
            'name': 'Tax 19%',
            'amount': 19,
            'type_tax_use': 'sale',
            'tax_group_id': self.tax_group_1.id,
            'tax_group_fe': 'iva_fe'
        })

        self.retention_tax = self.env['account.tax'].create({
            'name': 'TEST: RteFte -3.50% Ventas',
            'amount': -3.50,
            'type_tax_use': 'sale',
            'tax_group_id': self.tax_group_2.id,
            'tax_group_fe': 'other_fe'
        })

        self.retention_tax2 = self.env['account.tax'].create({
            'name': 'TEST: RteIVA 15% sobre el 19% IVA Ventas%',
            'amount': -15,
            'type_tax_use': 'sale',
            'tax_group_id': self.tax_group_2.id,
            'tax_group_fe': 'other_fe'
        })
        self.tax_zero = self.env['account.tax'].create({
            'name': 'Tax 0%',
            'amount': 0,
            'type_tax_use': 'sale',
            'tax_group_id': self.tax_group_1.id,
            'tax_group_fe': 'other_fe'
        })
        tax_lines = [
            self.tax.id,
            self.retention_tax.id,
            self.retention_tax2.id
        ]
        self.pay_terms_a = self.env.ref(
            'account.account_payment_term_immediate')
        self.salesperson = self.env.ref('base.user_admin')
        self.salesperson.function = 'Sales'
        self.invoice_dicc = {
            'type': 'out_invoice',
            'invoice_user_id': self.salesperson.id,
            'name': 'OC 123',
            'journal_id': self.sale_journal.id,
            'partner_id': self.partner.id,
            'commercial_partner_id': self.partner.id,
            'currency_id': self.company.currency_id.id,
            'invoice_payment_term_id': self.pay_terms_a.id,
            'line_ids': [(0, 0, {
                'account_id': self.account.id,
                'product_id': self.env.ref("product.product_product_4").id,
                'partner_id': self.partner.id,
                'credit': 660000,
                'price_unit': 660000,
                "tax_ids": [(6, 0, tax_lines)]
            }), (0, 0, {
                'account_id': self.account.id,
                'partner_id': self.partner.id,
                'tax_line_id': self.tax.id,
                'price_unit': 125400,
                'credit': 125400,
                'tax_base_amount': 660000,
                'name': "TEST: IVA Ventas 19%",
            }), (0, 0, {
                'account_id': self.account.id,
                'partner_id': self.partner.id,
                'tax_line_id': self.retention_tax.id,
                'price_unit': -23100,
                'debit': 23100,
                'tax_base_amount': 660000,
                'name': 'TEST: RteFte -3.50% Ventas',
            }), (0, 0, {
                'account_id': self.account.id,
                'partner_id': self.partner.id,
                'tax_line_id': self.retention_tax2.id,
                'price_unit': -18810,
                'debit': 18810,
                'tax_base_amount': 660000,
                'name': 'RteIVA 15% sobre el 19% IVA Ventas',
            }), (0, 0, {
                'account_id': self.account.id,
                'partner_id': self.partner.id,
                'debit': 743490,
                'price_unit': -743490,
            })],
            'invoice_line_ids': [(0, 0, {
                'product_id': self.env.ref("product.product_product_4").id,
                'quantity': 1,
                'account_id': self.account_sale.id,
                'price_unit': 660000,
                'credit': 660000,
                'partner_id': self.partner.id,
                "tax_ids": [(6, 0, tax_lines)]
            })],
        }

        dicc = {'id': 2832, 'name': 'TEST1', 'amount': 125400.0}
        self.act_field = self.ref_act_fields.create({
            'name': 'Field 1',
            'code': '001',
            'mandatory': 'required',
            'condition_python': 'result = ' + str(dicc),
        })
        self.act_field_2 = self.ref_act_fields.create({
            'name': 'Field 2',
            'code': '002',
            'mandatory': 'required',
            'condition_python': 'ERROR',
        })
        self.act_field_3 = self.ref_act_fields.create({
            'name': 'Field 3',
            'code': '003',
            'mandatory': 'required',
            'condition_python': 'result = account.invoice_line_ids',
        })

        self.act_field_4 = self.ref_act_fields.create({
            'name': 'Field 4',
            'code': '004',
            'mandatory': 'required',
            'condition_python': 'result = record.get("name")',
        })
        self.act_field_5 = self.ref_act_fields.create({
            'name': 'Field 5',
            'code': '005',
            'mandatory': 'required',
            'condition_python': 'result = record.get("amount")',
        })

        self.line_id = self.tech_provider_line.create({
            'name': 'Field line',
            'code': '001',
            'level': 0,
        })

        self.line_id_2 = self.tech_provider_line.create({
            'name': 'Field line 2',
            'code': '002',
            'level': 0,
            'parent_id': self.line_id.id,
            'act_field_id': self.act_field.id,
        })

        self.line_id_3 = self.tech_provider_line.create({
            'name': 'Field line 3',
            'code': '003',
            'level': 0,
            'act_field_id': self.act_field_3.id,
        })

        self.line_id_4 = self.tech_provider_line.create({
            'name': 'Field line 4',
            'code': '004',
            'level': 0,
            'parent_id': self.line_id_2.id,
            'act_field_id': self.act_field_4.id,
        })

        self.line_id_5 = self.tech_provider_line.create({
            'name': 'Field line 5',
            'code': '002',
            'level': 0,
            'parent_id': self.line_id_2.id,
            'act_field_id': self.act_field_5.id,
        })

        iva = self.ref_act_fields.search(
            [('code', '=', 'COD250')], limit=1).id

        rete = self.ref_act_fields.search(
            [('code', '=', 'COD250')], limit=1).id

        _module = 'l10n_co_act_fields.account_act_fields_'
        act_field_1 = self.env.ref(_module + '253')
        act_field_2 = self.env.ref(_module + '254')
        self.act_field_252 = self.env.ref(_module + '252')
        _module = 'l10n_co_tech_provider.l10n_co_tech_provider_line_headboard_'
        self.env.ref(_module + '07_1').write({
            'act_field_id': iva})

        self.env.ref(_module + '07_2').write({
            'act_field_id': rete})

        self.ref_act_fields.search([]).write({
            'mandatory': 'optional'})

        self.tech_provider_1 = self.tech_provider.search(
            [('code', '=', 'FAX')], limit=1)

        self.tax_type = self.TaxType.create({
            'code': 'TAX001',
            'name': 'TAX TEST',
            'retention': True,
        })

        self.responsability_2 = self.DianFiscalResp.search(
            [('code', '=', 'O-23')])
        self.tax_apply_1 = self.TaxType.create({
            'code': 'TEST1',
            'name': 'TEST1',
            'retention': False,
        })
        self.tax_apply_2 = self.TaxType.create({
            'code': 'TEST2',
            'name': 'TEST3',
            'retention': True,
        })

        self.account_payment = self.AccountPayment.create({
            'journal_id': self.sale_journal.id,
            'payment_type': "inbound",
            'partner_type': "customer",
            'amount': 2000000,
            'payment_date': datetime.now(),
            'partner_id': self.partner.id,
            'payment_method_id': self.env.ref(
                'account.account_payment_method_manual_out').id
        })
