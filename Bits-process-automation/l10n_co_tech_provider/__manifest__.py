# -*- coding: utf-8 -*-
{
    'name': "l10n_co_tech_provider",

    'summary': """
        module that manages technological providers of
        Colombian electronic billing
    """,

    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",

    'category': 'Uncategorized',
    'version': '13.0.1.0.0',
    'depends': [
        'base',
        'account',
        'l10n_co_e_invoice_act_fields',
        'bits_api_connect',
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/tech_provider_view.xml',
        'data/tech_provider_data.xml',
        'data/l10n_co.tech.provider.line.csv',
        'views/tech_provider_settings_view.xml',
    ],
}
