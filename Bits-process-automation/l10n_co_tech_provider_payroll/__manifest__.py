# -*- coding: utf-8 -*-
{
    'name': "l10n_co_tech_provider_payroll",

    'summary': """
        module that manages technological providers of
        Colombian electronic billing
    """,

    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",

    'category': 'Uncategorized',
    'version': '13.0.1.0.2',
    'depends': [
        'base',
        'hr_payroll',
        'l10n_co_tech_provider',
        'l10n_co_payroll_act_fields'
    ],

    'data': [
        'views/tech_provider_view.xml',
        'data/tech_provider_data.xml',
        'data/l10n_co.tech.provider.line.csv',
        'views/tech_provider_settings_view.xml',
    ],
}
