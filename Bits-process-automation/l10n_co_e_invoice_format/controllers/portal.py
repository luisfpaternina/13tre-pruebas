# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.addons.account.controllers.portal import PortalAccount
from odoo.exceptions import AccessError, MissingError
from odoo.http import request


class PortalAccount(PortalAccount):

    @http.route(
        ['/my/invoices/<int:invoice_id>'],
        type='http',
        auth="public",
        website=True)
    def portal_my_invoice_detail(self, invoice_id, access_token=None,
                                 report_type=None, download=False, **kw):
        try:
            invoice_sudo = self._document_check_access(
                'account.move', invoice_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        res = super(PortalAccount, self).portal_my_invoice_detail(
            invoice_id, access_token, report_type, download, **kw)
        if report_type in ('html', 'pdf', 'text'):
            _ref = 'l10n_co_e_invoice_format.l10n_co_e_invoice_format_report'
            return self._show_report(
                model=invoice_sudo,
                report_type=report_type,
                report_ref=_ref,
                download=download)
        return res
