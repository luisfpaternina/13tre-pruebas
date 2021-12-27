# -*- coding: utf-8 -*-
{
    'name': "account_account_level",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Accounting',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'account_accountant'
    ],

    # always loaded
    'data': [
        'views/account_account_level.xml',
    ]
}
