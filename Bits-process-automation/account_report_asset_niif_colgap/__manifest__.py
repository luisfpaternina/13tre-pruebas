# -*- coding: utf-8 -*-
{
    'name': "Account Report Asset Niif Colgap",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
Assets management
=================
Manage assets owned by a company or a person.
Keeps track of depreciations, and creates corresponding journal entries.

    """,

    'author': "Bits Americas S.A.S.",
    'website': "http://www.bitsamericas.com",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '13.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'account_reports',
        'account_asset_colgap',
        'account_journal_niif'
    ],

    # always loaded
    'data': [
        'reports/account_assets_report_niif_colgap_views.xml'
    ],
}
