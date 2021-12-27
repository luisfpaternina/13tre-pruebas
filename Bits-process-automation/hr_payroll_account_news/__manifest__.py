# -*- coding: utf-8 -*-
{
    'name': "Payroll Account News",

    'description': """
        This module divides news, if the settlement line has more than one
        news assigned
    """,

    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Payroll Account',
    'version': '13.0.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'hr_payroll_account_partner',
        'bits_hr_payroll_news_related'
    ],

    # always loaded
    'data': [

    ],
    # only loaded in demonstration mode
    'demo': []
}
