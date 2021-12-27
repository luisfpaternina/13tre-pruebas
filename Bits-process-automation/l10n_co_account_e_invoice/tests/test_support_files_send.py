# -*- coding: utf-8 -*-

from odoo.addons.l10n_co_account_e_invoice.tests.common \
    import TestFECommon
from odoo.exceptions import ValidationError

from base64 import b64encode


class TestSupportFilesSend(TestFECommon):

    def setUp(self):
        super(TestSupportFilesSend, self).setUp()
        self.wizard_ref = self.env['support.files.send']
        self.invoice_ref = self.env['account.move']
        self.attachment_ref = self.env['ir.attachment']
        content = """
            {
                'nombre': 'Pepito',
                'apellido': 'Perez',
                'edad': 12,
            }
        """
        content = content.encode('UTF-8')
        content_binary = b64encode(content)
        self.attach = self.attachment_ref.create(
            {
                'name': 'basic_information',
                'datas': content_binary,
                'type': 'binary',
                'mimetype': 'text/plain',
            }
        )

    def test_creation_wizard_without_files(self):
        invoice = self.invoice_ref.create(self.invoice_dicc)
        wizard = self.wizard_ref.with_context(
            invoice_id=invoice.id,
            message='The maximium files is 12'
        ).new()
        wizard._get_invoice_id()
        wizard._compute_message_wizard()
        wizard.action_post_support_files()

    def test_creation_wizard_whit_files(self):
        invoice = self.invoice_ref.create(self.invoice_dicc)
        wizard = self.wizard_ref.with_context(
            invoice_id=invoice.id,
            message='The maximium files is 12'
        ).new(
            {
                'attachment_ids': [(6, 0, [self.attach.id, ])]
            }
        )
        config = self.env['ir.config_parameter'].sudo()
        provider_tech = self.env.ref(
            'l10n_co_tech_provider.l10n_co_tech_provider_01'
        )
        config.set_param('l10n_co_tech_provider.provider_id', provider_tech.id)
        wizard._get_invoice_id()
        wizard._compute_message_wizard()
        wizard.action_post_support_files()

    def test_validate_error_max_fields(self):
        invoice = self.invoice_ref.create(self.invoice_dicc)
        content2 = """
            {
                'nombre': 'Jose',
                'apellido': 'Rincon',
                'edad': 29,
            }
        """
        content2 = content2.encode('UTF-8')
        content_binary2 = b64encode(content2)
        attach2 = self.attachment_ref.create(
            {
                'name': 'basic_information_jose',
                'datas': content_binary2,
                'type': 'binary',
                'mimetype': 'text/plain',
            }
        )
        wizard = self.wizard_ref.with_context(
            invoice_id=invoice.id,
            message='The maximium files is 12'
        ).new(
            {
                'attachment_ids': [
                    (6, 0, [self.attach.id, attach2.id])
                ]
            }
        )
        config = self.env['ir.config_parameter'].sudo()
        provider_tech = self.env.ref(
            'l10n_co_tech_provider.l10n_co_tech_provider_01'
        )
        config.set_param('l10n_co_tech_provider.provider_id', provider_tech.id)
        wizard._get_invoice_id()
        wizard._compute_message_wizard()
        with self.assertRaises(ValidationError):
            wizard.action_post_support_files()

    def test_validation_max_size(self):
        invoice = self.invoice_ref.create(self.invoice_dicc)
        wizard = self.wizard_ref.with_context(
            invoice_id=invoice.id,
            message='The maximium files is 12'
        ).new(
            {
                'attachment_ids': [(6, 0, [self.attach.id, ])]
            }
        )
        config = self.env['ir.config_parameter'].sudo()
        provider_tech = self.env.ref(
            'l10n_co_tech_provider.l10n_co_tech_provider_01'
        )
        provider_tech.write(
            {
                'maximum_megabytes': 0,
            }
        )
        config.set_param('l10n_co_tech_provider.provider_id', provider_tech.id)
        wizard._get_invoice_id()
        wizard._compute_message_wizard()
        with self.assertRaises(ValidationError):
            wizard.action_post_support_files()

    def test_action_post_support_files_without_provider(self):
        invoice = self.invoice_ref.create(self.invoice_dicc)
        wizard = self.wizard_ref.with_context(
            invoice_id=invoice.id,
            message='The maximium files is 12'
        ).new(
            {
                'attachment_ids': [(6, 0, [self.attach.id, ])]
            }
        )
        wizard._get_invoice_id()
        wizard._compute_message_wizard()
        with self.assertRaises(ValidationError):
            wizard.action_post_support_files()

    def test_get_default_reconcile_line_ids(self):
        self.account_payment.post()
        lines = self.account_payment.move_line_ids.filtered(
            lambda x: x.credit > 0 and x.debit == 0)
        invoice = self.invoice_ref.create(self.invoice_dicc)
        wizard = self.wizard_ref.with_context(
            invoice_id=invoice.id,
            message='The maximium files is 12'
        ).create({
            'reconcile_line_ids': [(6, 0, lines.ids)]
        })
        domain = wizard._get_default_reconcile_line_ids()
        wizard._get_invoice_id()
        wizard._onchange_invoice_id()
        wizard.action_post_support_files()

    def test_action_post_support_files_extra_refs(self):
        custom_fields = self.env.ref(
            'l10n_co_account_e_invoice.l10n_co_custom_fields_01')
        self.env['l10n_co.custom.fields'].search([('code', '=', 'COD250')])
        lines = [(0, 0, {
            'custom_field_id': custom_fields.id,
            'method_type': 'ON',
            'value': '123456789'
        })]
        invoice = self.invoice_ref.create(self.invoice_dicc)
        wizard = self.wizard_ref.with_context(
            invoice_id=invoice.id,
            message='The maximium files is 12'
        ).create({
            'line_ids': lines
        })
        wizard._get_invoice_id()
        wizard._onchange_invoice_id()
        wizard.action_post_support_files()
