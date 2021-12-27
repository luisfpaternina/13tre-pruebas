# -*- coding: utf-8 -*-
{
    'name': "l10n_co_e_invoice_format",

    'summary': """
        Management of personalized report, for electronic billing
    """,

    'author': "Bits Americas S.A.S",
    'website': "https://www.bitsamericas.com",

    'category': 'Uncategorized',
    'version': '13.0.0.1.0',

    'depends': ['base', 'l10n_co_account_e_invoice'],

    'data': [
        'security/ir.model.access.csv',
        'views/invoice_format_report.xml',
        'views/view_invoice.xml',
        'data/mail_template_data.xml',
    ],
}
