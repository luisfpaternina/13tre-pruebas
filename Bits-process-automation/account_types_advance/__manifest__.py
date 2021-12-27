# -*- coding: utf-8 -*-
{
    'name': "Account types advanced",

    'description': """
        Module for the correct creation of types of accounting accounts.
    """,

    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",

    'category': 'Uncategorized',
    'version': '13.0.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account_accountant'],

    # always loaded
    'data': [
        'views/views_account_type.xml',
    ],
    'auto_install': True,
    'installable': True,
}
