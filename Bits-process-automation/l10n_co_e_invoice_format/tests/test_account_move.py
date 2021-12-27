from datetime import date, datetime, timedelta
from odoo.addons.l10n_co_account_e_invoice.tests.common \
    import TestFECommon
from odoo.exceptions import UserError, MissingError, ValidationError

from odoo.addons.l10n_co_e_invoice_format.controllers.portal \
    import PortalAccount

from unittest.mock import patch, Mock
from odoo.addons.website.tools import MockRequest

from odoo.addons.bits_api_connect.models.api_connection\
    import ApiConnectionRequest, ApiConnectionException


class TestAccountMove(TestFECommon):

    def setUp(self):
        super(TestAccountMove, self).setUp()

    def test_action_invoice_sent(self):
        invoice = self.env['account.move'].create(self.invoice_dicc)
        invoice.action_invoice_sent()

        template = self.env.ref(
            'l10n_co_e_invoice_format.email_template_edi_invoice_fe_invoice',
            raise_if_not_found=False)

        template.write({
            'lang': False
        })

        invoice.action_invoice_sent()

    def test_action_portal_my_invoice_detail(self):
        invoice = self.env['account.move'].create(self.invoice_dicc)
        controller = PortalAccount()
        return_value = {
            'status': 'accepted',
            'transaccionID': '00000001',
        }
        url = ('odoo.addons.account.controllers.portal.PortalAccount'
               '.portal_my_invoice_detail')
        url2 = ('odoo.addons.portal.controllers.portal.CustomerPortal'
                '._show_report')
        url3 = ('odoo.addons.portal.controllers.portal.CustomerPortal'
                '._document_check_access')

        with MockRequest(self.env):
            with patch(url, new=Mock(return_value=return_value)),\
                 patch(url2, new=Mock(return_value=return_value)):
                controller.portal_my_invoice_detail(
                    invoice.id, invoice._portal_ensure_token(),
                    report_type='pdf')

                controller.portal_my_invoice_detail(
                    invoice.id, invoice._portal_ensure_token())

        def return_raise(
            self, model_name, document_id, access_token=None
        ):
            raise MissingError("This document does not exist.")

        with MockRequest(self.env):
            with patch(url3, new=return_raise):
                controller.portal_my_invoice_detail(
                    invoice.id)
