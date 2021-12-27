# -*- coding: utf-8 -*-
{
    'name': "bits_purchase_account",

    'summary': """
        This module add register payment validation
        Add approval button to approve payment
    """,

    'author': "Bits Americas",
    'website': "http://www.bitsamericas.com",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Accounting/Accounting',
    'version': '13.0.1.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'security_restrict_action_function'
    ],

    # always loaded
    'data': [
        'data/actions_restrict.xml',
        'views/views.xml'
    ],

    'installable': True,
}
