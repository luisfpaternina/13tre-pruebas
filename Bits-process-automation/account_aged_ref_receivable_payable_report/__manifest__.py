# -*- coding: utf-8 -*-
{
    'name': "Account Overdue Recivable Payable Report",

    'summary': """
        This module add field reference the invoices and journal entries""",


    'author': "Bits Americas",
    'website': "http://www.bitsamericas.com",

    'category': 'Accountasnt',
    'version': '13.0.1.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'account_asset',
        'account_reports'
    ],

    # always loaded
    'data': [

    ],
    # 'auto_install': True,
    'installable': True,
}
