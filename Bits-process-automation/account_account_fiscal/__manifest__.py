# -*- coding: utf-8 -*-
{
    'name': "Account Account Fiscal",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Bits Americas S.A.S",
    'website': "http://www.bitsamericas.com",

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
        # 'security/ir.model.access.csv',
        'views/account_account_niif.xml',
        'views/res_config_settings.xml',
    ],
    'installable': True,
    'auto_install': False,
}
