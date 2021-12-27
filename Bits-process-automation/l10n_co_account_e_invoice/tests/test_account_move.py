from datetime import date, datetime, timedelta
from odoo.addons.l10n_co_account_e_invoice.tests.common \
    import TestFECommon
from odoo.exceptions import UserError, MissingError, ValidationError
from odoo.addons.l10n_co_account_e_invoice.models.browsable_object \
    import Invoive
from odoo.tests import tagged
from odoo import fields
from unittest.mock import patch, Mock
from odoo.tests.common import Form
from requests.exceptions import ConnectionError
from odoo.addons.bits_api_connect.models.connections.api_connection\
    import ApiConnectionException


@tagged('post_install', '-at_install')
class TestAccountMove(TestFECommon):

    def setUp(self):
        super(TestAccountMove, self).setUp()

    def test_create_account_move_create_invoice(self):
        invoice = self.env['account.move'].create(self.invoice_dicc)
        type_doc = invoice._get_ei_type_document_id()
        self.assertTrue(type_doc)
        invoice._compute_is_direct_payment()
        invoice._upload_message_electronic_invoice()

    def test_generate_dict_invoice_dian(self):
        invoice = self.env['account.move'].create(self.invoice_dicc)
        invoice.action_test()

    def test_get_template_code_description(self):
        res = self.company._get_template_code_description()
        self.assertEqual(res, 'CGEN03')

    def test_get_data_taxes_e_invoice_line(self):
        invoice = self.env['account.move'].create(self.invoice_dicc)

        for line in invoice.invoice_line_ids:
            line.write({
                'tax_ids': [(6, 0, [self.tax.id, self.retention_tax.id])]
            })
        res = line._get_data_taxes_e_invoice_line()
        self.assertEqual(len(res), 0)
        res = line._get_data_taxes_e_invoice_line(name='IVA')
        self.assertEqual(len(res), 15)

        invoice.amount_by_group = [(
            self.tax_group_1.name, 200,
            1000,
            self.tax_group_1.id
        )]

        res = invoice._get_tax_by_group('IVA')
        res = invoice._get_tax_by_group('IVA02')

    def test_action_post_without_fe(self):
        invoice = self.env['account.move'].create(self.invoice_dicc)
        invoice.action_post()

    def test_action_post_active_tech_provider(self):
        invoice = self.env['account.move'].create(self.invoice_dicc)
        config = self.env['res.config.settings'].create({})
        config.active_tech_provider = True
        config.execute()

        return_value = {
            'status': 'accepted',
            'transaccionID': '00000001',
        }
        url = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.upload')
        with patch(url, new=Mock(return_value=return_value)):
            with self.assertRaises(UserError):
                invoice.action_post()

    def test_action_post_other_document_type(self):
        config = self.env['res.config.settings'].create({})
        config.active_tech_provider = True
        config.provider_id = self.tech_provider_1.id
        config.execute()
        self.account_journal = self.env['account.journal'].create({
            'name': 'account journal test',
            'code': 'NOM',
            'type': 'general'
        })

        move = self.env['account.move'].create({
            'ref': 'Nomina Test',
            'date': datetime.now(),
            'journal_id': self.account_journal.id,
            'line_ids': [
                (0, 0, {
                    'account_id': self.account_sale.id,
                    'debit': 300,
                    'name': 'Furniture',
                }),
                (0, 0, {
                    'account_id': self.account_sale.id,
                    'credit': 300,
                }),
            ]
        })

        move.action_post()

    def test_action_post_with_fe_error(self):

        def _create_fe_tech_provider(
            self, _type, filename, file, attachments=False
        ):
            raise ApiConnectionException('Error')

        invoice = self.env['account.move'].create(self.invoice_dicc)
        config = self.env['res.config.settings'].create({})
        config.active_tech_provider = True
        config.provider_id = self.tech_provider_1.id
        config.execute()

        url = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.upload')
        url2 = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.__init__')

        with patch(url, new=_create_fe_tech_provider),\
             patch(url2, new=Mock(return_value=None)):
            with self.assertRaises(UserError):
                invoice.with_context(not_auto_commit=True).action_post()

    def test_action_get_document_tech_provider_error(self):
        def _download_fe_tech_provider(self, _type, idTransaccion):
            return False, {'response': {'representacionGrafica': 'YWJj'}}, True
        config = self.env['res.config.settings'].create({})
        config.active_tech_provider = True
        config.provider_id = self.tech_provider_1.id
        config.execute()
        return_value = {}
        invoice = self.env['account.move'].create(self.invoice_dicc)
        url = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.download')
        url2 = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.__init__')
        with self.assertRaises(ValidationError):
            with patch(url, new=_download_fe_tech_provider),\
                 patch(url2, new=Mock(return_value=None)):
                invoice.action_test_api_connect()

    def test_create_account_move_raise_out_refund(self):
        invoice_dicc = {
            'type': 'out_refund',
            'ei_origin_id': False,
            'invoice_user_id': self.salesperson.id,
            'name': 'OC 123',
            'journal_id': self.sale_journal.id,
            'partner_id': self.partner.id,
            'currency_id': self.company.currency_id.id,
            'line_ids': [(0, 0, {
                'account_id': self.account.id,
                'partner_id': self.partner.id,
                'tax_line_id': self.tax.id,
                'debit': 1000,
            }), (0, 0, {
                'account_id': self.account.id,
                'partner_id': self.partner.id,
                'tax_line_id': self.retention_tax.id,
                'credit': 1000,
            })],
            'invoice_line_ids': [(0, 0, {
                'product_id': self.env.ref("product.product_product_4").id,
                'quantity': 1,
                'account_id': self.account_sale.id,
                'price_unit': 1000,
                'partner_id': self.partner.id,
                'tax_ids': [(6, 0, self.tax.ids)],
            })],
        }
        invoice = self.env['account.move'].create(invoice_dicc)
        config = self.env['res.config.settings'].create({})
        config.active_tech_provider = True
        config.provider_id = self.tech_provider_1.id
        config.execute()
        with self.assertRaises(UserError):
            invoice.action_post()

    def test_post_with_files_without_provider(self):
        move = self.invoice_dicc.copy()
        move['type'] = 'out_refund'
        invoice2 = self.env['account.move'].create(move)
        with self.assertRaises(ValidationError):
            invoice2.action_post_with_files()

    def test_post_with_files_with_provider(self):
        move = self.invoice_dicc.copy()
        move['type'] = 'out_refund'
        invoice2 = self.env['account.move'].create(move)
        config = self.env['res.config.settings'].create({})
        config.active_tech_provider = True
        config.provider_id = self.tech_provider_1.id
        config.execute()
        invoice2.action_post_with_files()

    def test_onchange_partner_id_invoice(self):
        invoice = self.env['account.move'].create(self.invoice_dicc)
        invoice._onchange_partner_id()

    def test_action_get_document_tech_provider_error1(self):
        invoice_dicc = self.invoice_dicc.copy()

        def _download_fe_tech_provider(self, _type, idTransaccion):
            return True, {'response': {'representacionGrafica': 'YWJj'}}, False
        config = self.env['res.config.settings'].create({})
        config.active_tech_provider = True
        config.provider_id = self.tech_provider_1.id
        config.execute()
        invoice_dicc['ei_number'] = '17662647'
        invoice = self.env['account.move'].create(invoice_dicc)
        url = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.download')
        url2 = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.__init__')
        with patch(url, new=_download_fe_tech_provider),\
             patch(url2, new=Mock(return_value=None)):
            invoice.action_test_api_connect()

    def test_invoice_tax_validations(self):
        self.tax.write({'type_of_tax': self.tax_apply_1.id})
        self.retention_tax.write({'type_of_tax': self.tax_type.id})
        self.retention_tax2.write({'type_of_tax': self.tax_type.id})

        move = self.invoice_dicc.copy()
        data = self.invoice_dicc.copy()
        invoice = self.env['account.move'].create(move)
        config = self.env['res.config.settings'].create({})
        config.active_tech_provider = True
        config.provider_id = self.tech_provider_1.id
        config.execute()
        return_value = {
            'status': 'accepted',
            'transaccionID': '00000001',
        }

        _module = 'l10n_co_act_fields.account_act_fields_'
        self.env.ref(_module + '189').write({
            'condition_select': 'python',
            'validate_condition_select': 'result = False'})

        url = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.upload')
        url2 = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.__init__')
        with patch(url, new=Mock(return_value=return_value)),\
             patch(url2, new=Mock(return_value=None)):
            invoice.action_post()

    def test_invoice_tax_validations_2(self):
        self.tax.write({'type_of_tax': self.tax_apply_1.id})
        self.retention_tax.write({'type_of_tax': self.tax_type.id})
        self.retention_tax2.write({'type_of_tax': self.tax_type.id})

        move = self.invoice_dicc.copy()
        invoice = self.env['account.move'].create(move)
        config = self.env['res.config.settings'].create({})
        config.active_tech_provider = True
        config.provider_id = self.tech_provider_1.id
        config.execute()
        return_value = {
            'status': 'accepted',
            'transaccionID': '00000001',
        }

        self.line_id.write({
            'tech_provider_id': self.tech_provider_1.id})

        url = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.upload')
        url2 = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.__init__')
        with patch(url, new=Mock(return_value=return_value)),\
             patch(url2, new=Mock(return_value=None)):
            invoice.action_post()

    def test_get_dict_by_group(self):
        self.tax.write({'type_of_tax': self.tax_apply_1.id})
        self.retention_tax.write({'type_of_tax': self.tax_type.id})
        self.retention_tax2.write({'type_of_tax': self.tax_type.id})
        move = self.invoice_dicc.copy()
        invoice = self.env['account.move'].create(move)
        config = self.env['res.config.settings'].create({})
        config.active_tech_provider = True
        config.provider_id = self.tech_provider_1.id
        config.execute()
        return_value = {
            'status': 'accepted',
            'transaccionID': '00000001',
        }
        for line in invoice.line_ids:
            line.write({
                'currency_id': invoice.company_id.currency_id.id,
                'tax_line_id': self.tax.id
            })
        invoice._get_dict_by_group()

    def test_action_get_document_tech_provider_error2(self):
        invoice_dicc = self.invoice_dicc.copy()

        def _download_fe_tech_provider(self, _type, idTransaccion):
            return True, {'response': {}}, False
        config = self.env['res.config.settings'].create({})
        config.active_tech_provider = True
        config.provider_id = self.tech_provider_1.id
        config.execute()
        invoice_dicc['ei_number'] = '17662647'
        invoice = self.env['account.move'].create(invoice_dicc)
        url = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.download')
        url2 = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.__init__')
        with patch(url, new=_download_fe_tech_provider),\
             patch(url2, new=Mock(return_value=None)):
            invoice.action_test_api_connect()

    def test_invoice_tax_validations_3(self):
        self.tax.write({'type_of_tax': self.tax_apply_1.id})
        self.retention_tax.write({'type_of_tax': self.tax_type.id})
        self.retention_tax2.write({'type_of_tax': self.tax_type.id})

        move = self.invoice_dicc.copy()
        invoice = self.env['account.move'].create(move)
        config = self.env['res.config.settings'].create({})
        config.active_tech_provider = True
        config.provider_id = self.tech_provider_1.id
        config.execute()
        return_value = {
            'status': 'accepted',
            'transaccionID': '00000001',
        }

        self.act_field.write({
            'condition_python': 'result = ' + str({})})

        self.line_id.write({
            'tech_provider_id': self.tech_provider_1.id})

        url = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.upload')
        url2 = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.__init__')
        with patch(url, new=Mock(return_value=return_value)),\
             patch(url2, new=Mock(return_value=None)):
            invoice.action_post()

    def test_get_surchange_discount_data(self):
        move = self.invoice_dicc.copy()
        invoice = self.env['account.move'].create(move)
        inv = Invoive(invoice.partner_id.id, invoice, invoice.env)
        inv._get_surchange_discount_data()
        invoice._get_surchange_discount_data()
        for line in invoice.invoice_line_ids:
            line._get_surchange_discount_by_line()

    def test_action_cron_get_document_invoices(self):
        invoice_dicc = self.invoice_dicc.copy()

        def _download_fe_tech_provider(self, _type, idTransaccion):
            response = {
                'response': {
                    'representacionGrafica': 'YWJj',
                    'representacionGraficaAppResponse': 'YWJj',
                    'appResponse': 'YWJj',
                    'ubl': 'YWJj',
                    'estatusDocumento': ''
                }
            }
            return True, response, False

        def _download_fe_tech_provider2(self, _type, idTransaccion):
            return True, {'response': {}}, False
        move = self.invoice_dicc.copy()
        invoice = self.env['account.move'].create(move)
        url3 = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.__init__')
        with patch(url3, new=Mock(return_value=None)):
            invoice.action_cron_get_document_invoices()

        config = self.env['res.config.settings'].create({})
        config.active_tech_provider = True
        config.provider_id = self.tech_provider_1.id
        config.execute()

        return_value = {
            'status': 'accepted',
            'transaccionID': '00000001',
        }

        url = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.upload')
        with patch(url, new=Mock(return_value=return_value)),\
             patch(url3, new=Mock(return_value=None)):
            invoice.action_post()

        url2 = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.download')
        with patch(url2, new=_download_fe_tech_provider2),\
             patch(url3, new=Mock(return_value=None)):
            invoice.action_cron_get_document_invoices()

        with patch(url2, new=_download_fe_tech_provider),\
             patch(url3, new=Mock(return_value=None)):
            invoice.action_cron_get_document_invoices()

        invoice_dicc['ei_number'] = '17662647'
        invoice2 = self.env['account.move'].create(invoice_dicc)
        url = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.download')
        with patch(url, new=_download_fe_tech_provider),\
             patch(url3, new=Mock(return_value=None)):
            invoice2.action_cron_get_document_invoices()

    def test_action_post_return_rejected(self):
        invoice = self.env['account.move'].create(self.invoice_dicc)
        config = self.env['res.config.settings'].create({})
        config.active_tech_provider = True
        config.provider_id = self.tech_provider_1.id
        config.execute()

        return_value = {
            'status': 'rejected',
            'transaccionID': '00000001',
        }

        def _create_api_conection(self, company, username,
                                  password, url_connection):
            raise ConnectionError

        url = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.upload')
        url3 = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.__init__')
        with patch(url, new=Mock(return_value=return_value)),\
             patch(url3, new=Mock(return_value=None)):
            with self.assertRaises(UserError):
                invoice.with_context(not_auto_commit=True).action_post()

    def test_l10n_co_log_rejected_invoice(self):
        invoice = self.env['account.move'].create(self.invoice_dicc)
        config = self.env['res.config.settings'].create({})
        config.active_tech_provider = True
        config.provider_id = self.tech_provider_1.id
        config.execute()

        return_value = {
            'status': 'rejected',
            'transaccionID': '00000001',
        }
        url = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.upload')
        url3 = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.__init__')
        with patch(url, new=Mock(return_value=return_value)),\
             patch(url3, new=Mock(return_value=None)):
            with self.assertRaises(MissingError):
                invoice.with_context(not_auto_commit=False).action_post()

    def test_bytes_action_cron_get_document_invoices(self):
        invoice_dicc = self.invoice_dicc.copy()

        def _download_fe_tech_provider(self, _type, idTransaccion):
            response = {
                'response': {
                    'representacionGrafica': bytes("TEST", 'utf-8'),
                    'representacionGraficaAppResponse': bytes("TEST", 'utf-8'),
                    'appResponse': bytes("TEST", 'utf-8'),
                    'ubl': bytes("TEST", 'utf-8'),
                    'estatusDocumento': ''
                }
            }
            return True, response, False
        move = self.invoice_dicc.copy()
        invoice = self.env['account.move'].create(move)

        url3 = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.__init__')
        with patch(url3, new=Mock(return_value=None)):
            invoice.action_cron_get_document_invoices()

        config = self.env['res.config.settings'].create({})
        config.active_tech_provider = True
        config.provider_id = self.tech_provider_1.id
        config.execute()

        return_value = {
            'status': 'accepted',
            'transaccionID': '00000001',
        }

        url = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.upload')
        with patch(url, new=Mock(return_value=return_value)),\
             patch(url3, new=Mock(return_value=None)):
            invoice.action_post()

        url2 = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.download')
        with patch(url2, new=_download_fe_tech_provider),\
             patch(url3, new=Mock(return_value=None)):
            invoice.action_cron_get_document_invoices()
            invoice.action_test_api_connect()

    def test_create_account_move_get_zero_taxes(self):
        invoice = self.env['account.move'].create(self.invoice_dicc)
        config = self.env['res.config.settings'].create({})
        config.active_tech_provider = True
        config.provider_id = self.tech_provider_1.id
        config.execute()
        for line in invoice.invoice_line_ids:
            line.write({
                'tax_ids': [(6, 0, [self.tax_zero.id, self.retention_tax.id])]
            })
        invoice._get_zero_taxes()

    def _create_credit_debit_note(self, invoice, data):
        data.update({
            'move_id': invoice.id
        })
        refund_wizard = self.env['account.move.reversal'].with_context(
            active_ids=[invoice.id], active_model='account.move').create(data)
        refund_wizard._compute_from_moves()
        res = refund_wizard.reverse_moves()
        refund = self.env['account.move'].browse(res['res_id'])
        return refund

    def test_create_credit_note(self):
        invoice = self.env['account.move'].create(self.invoice_dicc)
        config = self.env['res.config.settings'].create({})
        config.active_tech_provider = True
        config.provider_id = self.tech_provider_1.id
        config.execute()

        return_value = {
            'status': 'accepted',
            'transaccionID': '00000001',
        }

        url = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.upload')
        url3 = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.__init__')
        with patch(url, new=Mock(return_value=return_value)),\
             patch(url3, new=Mock(return_value=None)):
            invoice.action_post()

        code_credit = self.ref_code_desc.search(
            [('code', '=', '6')], limit=1)

        data_wizard = {
            '_type': 'credit_note',
            'description_code_credit': code_credit.id,
        }
        refund = self._create_credit_debit_note(invoice, data_wizard)
        refund._get_ei_type_dian()

    def test_create_credit_note_in(self):
        move = self.invoice_dicc.copy()
        move['type'] = 'in_invoice'
        invoice = self.env['account.move'].create(move)
        config = self.env['res.config.settings'].create({})
        config.active_tech_provider = True
        config.provider_id = self.tech_provider_1.id
        config.execute()

        return_value = {
            'status': 'accepted',
            'transaccionID': '00000001',
        }

        url = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.upload')
        url3 = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.__init__')
        with patch(url, new=Mock(return_value=return_value)),\
             patch(url3, new=Mock(return_value=None)):
            invoice.action_post()

        refund = self._create_credit_debit_note(invoice, {})
        refund._get_ei_type_dian()

    def test_action_cron_get_acceptance_status(self):
        invoice_dicc = self.invoice_dicc.copy()
        invoice = self.env['account.move'].create(invoice_dicc)

        config = self.env['res.config.settings'].create({})
        config.active_tech_provider = True
        config.provider_id = self.tech_provider_1.id
        config.execute()

        url3 = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.__init__')

        with patch(url3, new=Mock(return_value=None)):
            invoice.action_cron_get_acceptance_status()

        return_value = {
            'status': 'accepted',
            'transaccionID': '00000001',
        }

        url = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.upload')

        with patch(url, new=Mock(return_value=return_value)),\
             patch(url3, new=Mock(return_value=None)):
            invoice.action_post()

        url2 = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.validate_status')

        with patch(url2, new=Mock(return_value="Fiscalmente Valido")),\
             patch(url3, new=Mock(return_value=None)):
            invoice.action_cron_get_acceptance_status()

        with patch(url2, new=Mock(return_value=False)),\
             patch(url3, new=Mock(return_value=None)):
            invoice.action_cron_get_acceptance_status()

        with patch(url2, new=Mock(return_value="Fiscalmente Valido")),\
             patch(url3, new=Mock(return_value=None)):
            invoice.action_cron_get_acceptance_status()

    def test_validate_final_acceptance_status(self):
        sequences = self.env['ir.sequence'].search([], limit=2)
        sequence = False
        for seq in sequences:
            sequence = seq.id
        sale_journal = self.env['account.journal'].create({
            'name': 'reflets',
            'code': 'refin',
            'type': 'sale',
            'company_id': self.company.id,
            'sequence_id': sequence,
            'default_credit_account_id': self.account_sale.id,
            'default_debit_account_id': self.account_sale.id
        })
        invoice_dicc = self.invoice_dicc.copy()
        invoice_dicc['ei_invoice_datetime'] = (
            fields.Datetime.now() -
            timedelta(
                days=self.tech_provider_1.num_of_days_to_validate + 1
            )
        )
        invoice_dicc2 = invoice_dicc.copy()
        invoice_dicc['ei_status_message'] = "Enviado a Adquiriente"

        invoice2 = self.env['account.move'].create(self.invoice_dicc)
        invoice2.validate_final_acceptance_status()
        invoice = self.env['account.move'].create(invoice_dicc)
        invoice_dicc2['ei_status_message'] = "Aceptado"
        invoice_dicc2['journal_id'] = sale_journal.id

        invoice3 = self.env['account.move'].create(invoice_dicc2)

        config = self.env['res.config.settings'].create({})
        config.active_tech_provider = True
        config.provider_id = self.tech_provider_1.id
        config.execute()

        return_value = {
            'status': 'accepted',
            'transaccionID': '00000001',
        }

        url = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.upload')
        url3 = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.__init__')

        with patch(url, new=Mock(return_value=return_value)),\
             patch(url3, new=Mock(return_value=None)):
            invoice.action_post()

        with patch(url, new=Mock(return_value=return_value)),\
             patch(url3, new=Mock(return_value=None)):
            invoice3.action_post()

        url2 = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.validate_status')
        with patch(url2, new=Mock(return_value="Fiscalmente Valido")),\
             patch(url3, new=Mock(return_value=None)):
            invoice.action_cron_get_acceptance_status()

        with patch(url2, new=Mock(return_value=False)),\
             patch(url3, new=Mock(return_value=None)):
            invoice.validate_final_acceptance_status()

    def test_get_total_type_transferred(self):
        move = self.invoice_dicc.copy()
        move['type'] = 'in_invoice'
        invoice = self.env['account.move'].create(move)
        invoice._get_total_type_transferred()

        self.tax.write({
            'tax_group_fe': 'nap_fe',
        })

        for line in invoice.invoice_line_ids:
            line._get_computed_taxes()
            line._get_taxes_by_type()

    def test_post_config_trm_day(self):
        move = self.invoice_dicc.copy()
        move['currency_id'] = self.env.ref('base.USD').id
        invoice = self.env['account.move'].create(move)
        config = self.env['res.config.settings'].create({})
        config.active_tech_provider = True
        config.provider_id = self.tech_provider_1.id
        config.execute()
        _date = datetime.now()-timedelta(days=10)
        invoice.currency_id.write({'date': _date.date()})

        return_value = {
            'status': 'accepted',
            'transaccionID': '00000001',
        }

        url = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.upload')
        url3 = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.__init__')

        with patch(url, new=Mock(return_value=return_value)),\
             patch(url3, new=Mock(return_value=None)):
            with self.assertRaises(UserError):
                invoice.action_post()

    def test_action_post_with_fe_error_connection1(self):

        def _create_api_conection(self, company, username,
                                  password, url_connection):
            raise ConnectionError

        invoice = self.env['account.move'].create(self.invoice_dicc)
        config = self.env['res.config.settings'].create({})
        config.active_tech_provider = True
        config.provider_id = self.tech_provider_1.id
        config.execute()

        url = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.__init__')
        with patch(url, new=_create_api_conection):
            with self.assertRaises(UserError):
                invoice.with_context(not_auto_commit=True).action_post()

    def test_action_post_with_fe_error_connection2(self):

        def _create_api_conection(self, company, username,
                                  password, url_connection):
            raise ConnectionError

        invoice = self.env['account.move'].create(self.invoice_dicc.copy())
        config = self.env['res.config.settings'].create({})
        config.active_tech_provider = True
        config.provider_id = self.tech_provider_1.id
        config.execute()

        url = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.__init__')
        with patch(url, new=_create_api_conection):
            with self.assertRaises(MissingError):
                invoice.action_post()

    def test_invoice_tax_group_id_required(self):
        self.tax.write({'type_of_tax': self.tax_apply_1.id})
        self.retention_tax.write({'type_of_tax': self.tax_type.id})
        self.retention_tax2.write({'type_of_tax': self.tax_type.id})

        move = self.invoice_dicc.copy()
        invoice = self.env['account.move'].create(move)
        config = self.env['res.config.settings'].create({})
        config.active_tech_provider = True
        config.provider_id = self.tech_provider_1.id
        config.tax_group_id = self.tax_group_1.id
        config.execute()
        return_value = {
            'status': 'accepted',
            'transaccionID': '00000001',
        }

        self.line_id.write({
            'tech_provider_id': self.tech_provider_1.id})

        url = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.upload')
        url3 = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.__init__')

        with patch(url, new=Mock(return_value=return_value)),\
             patch(url3, new=Mock(return_value=None)):
            with self.assertRaises(UserError):
                invoice.action_post()

        invoice2 = self.env['account.move'].create({})
        invoice2.validate_required_tax()

    def test_validate_final_acceptance_status_multi_and_one(self):
        invoice_dicc = self.invoice_dicc.copy()
        invoice_dicc2 = self.invoice_dicc.copy()
        invoice_dicc2['name'] = 'OC 456'

        invoice_dicc['ei_invoice_datetime'] = (
            fields.Datetime.now() -
            timedelta(
                days=self.tech_provider_1.num_of_days_to_validate + 1
            )
        )
        invoice_dicc2['ei_invoice_datetime'] = (
            fields.Datetime.now() -
            timedelta(
                days=self.tech_provider_1.num_of_days_to_validate + 1
            )
        )

        invoice = self.env['account.move'].create(invoice_dicc)
        invoice2 = self.env['account.move'].create(invoice_dicc2)
        invoices = self.env['account.move'].search(
            ['|', ('id', '=', invoice.id), ('id', '=', invoice2.id)]
        )

        config = self.env['res.config.settings'].create({})
        config.active_tech_provider = True
        config.provider_id = self.tech_provider_1.id
        config.execute()

        return_value = {
            'status': 'accepted',
            'transaccionID': '00000001',
        }

        url = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.upload')
        url2 = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.validate_status')
        url3 = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.__init__')

        with patch(url, new=Mock(return_value=return_value)),\
             patch(url3, new=Mock(return_value=None)):
            invoices.action_post()

        with patch(url2, new=Mock(return_value=False)),\
             patch(url3, new=Mock(return_value=None)):
            invoices.validate_final_acceptance_status()

    def test_action_post_active_reconcile_line_ids(self):
        self.account_payment.post()
        lines = self.account_payment.move_line_ids.filtered(
            lambda x: x.credit > 0 and x.debit == 0)
        move = self.invoice_dicc.copy()
        move['advances_line_ids'] = [(6, 0, lines.ids)]
        invoice = self.env['account.move'].create(self.invoice_dicc)
        config = self.env['res.config.settings'].create({})
        config.active_tech_provider = True
        config.execute()
        invoice.advances_line_ids = lines
        invoice._compute_ei_amount_text()

        return_value = {
            'status': 'accepted',
            'transaccionID': '00000001',
        }

        url = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.upload')
        with patch(url, new=Mock(return_value=return_value)):
            with self.assertRaises(UserError):
                invoice.action_post()
        res = invoice._get_advance_values()
        self.assertEqual(len(res), 1)

    def test_create_debit_note(self):
        invoice_dicc = self.invoice_dicc.copy()
        invoice_dicc['company_id'] = self.company.id
        invoice = self.env['account.move'].create(invoice_dicc)
        config = self.env['res.config.settings'].create({})
        config.active_tech_provider = True
        config.provider_id = self.tech_provider_1.id
        type_document = self.env.ref(
            'l10n_co_account_e_invoice.l10n_co_type_documents_6'
        )
        config.update({
            'type_documents_for_debit_note': (4, type_document.id)
        })
        config.execute()

        return_value = {
            'status': 'accepted',
            'transaccionID': '00000001',
        }

        url = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.upload')
        url2 = ('odoo.addons.l10n_co_account_e_invoice.models.'
                'account_move.AccountInvoice._compute_amount')
        url3 = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.__init__')
        with patch(url, new=Mock(return_value=return_value)),\
             patch(url3, new=Mock(return_value=None)):
            invoice.action_post()

        code_credit = self.ref_code_desc.search(
            [('code', '=', '6')], limit=1)

        data_wizard = {
            '_type': 'debit_note',
            'description_code_debit': code_credit.id,
        }
        with patch(url2, new=Mock(return_value=None)):
            debit_note = self._create_credit_debit_note(invoice, data_wizard)
            debit_note.update({
                'company_id': self.company.id
            })
            debit_note.compute_debit_credit_note_visible()

    def test_create_credit_note(self):
        invoice_dicc = self.invoice_dicc.copy()
        invoice_dicc['company_id'] = self.company.id
        invoice = self.env['account.move'].create(invoice_dicc)
        config = self.env['res.config.settings'].create({})
        config.active_tech_provider = True
        config.provider_id = self.tech_provider_1.id
        type_document = self.env.ref(
            'l10n_co_account_e_invoice.l10n_co_type_documents_5'
        )
        config.update({
            'type_documents_for_credit_note': (4, type_document.id)
        })
        config.execute()

        return_value = {
            'status': 'accepted',
            'transaccionID': '00000001',
        }

        url = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.upload')
        url2 = ('odoo.addons.l10n_co_account_e_invoice.models.'
                'account_move.AccountInvoice._compute_amount')
        url3 = ('odoo.addons.bits_api_connect.models.connections'
               '.api_connection_facturaxion.ApiConnectionRequestFacturaxion'
               '.__init__')
        with patch(url, new=Mock(return_value=return_value)),\
             patch(url3, new=Mock(return_value=None)):
            invoice.action_post()

        code_credit = self.ref_code_desc.search(
            [('code', '=', '6')], limit=1)

        data_wizard = {
            '_type': 'credit_note',
            'description_code_credit': code_credit.id,
        }
        with patch(url2, new=Mock(return_value=None)):
            debit_note = self._create_credit_debit_note(invoice, data_wizard)
            debit_note.update({
                'company_id': self.company.id
            })
            debit_note.compute_debit_credit_note_visible()
            debit_note._get_total_advance()

    def test_compute_amount_to_show(self):
        move = self.invoice_dicc.copy()
        move['type'] = 'in_invoice'
        invoice = self.env['account.move'].create(move)
        invoice._get_total_type_transferred()

        self.tax.write({
            'tax_group_fe': 'nap_fe',
        })

        for line in invoice.invoice_line_ids:
            line._compute_amount_to_show()

    def test_get_computed_name(self):
        move = self.invoice_dicc.copy()
        invoice = self.env['account.move'].create(move)
        for line in invoice.invoice_line_ids:
            line._get_computed_name()
        invoice.ref = "TEST"
        for line in invoice.invoice_line_ids:
            line._get_computed_name()
