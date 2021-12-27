# -*- coding: utf-8 -*-
{
    'name': "Account General Ledger Analytic Account",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        in english
    """,

    'author': "Bits Americas",
    'website': "http://www.bitsamericas.com",

    'category': 'Accountasnt',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'account',
        'account_reports'
        ],

    # always loaded
    'data': [
        
    ],    
    # 'auto_install': True,
    'installable': True,
}
