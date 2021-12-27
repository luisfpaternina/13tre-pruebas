# -*- coding: utf-8 -*-
{
    'name': "purchase_order_report",

    'summary': """
        New default filter in Purchase Report
    """,

    'description': """
        This module modifies default filter in Purchase
        report adding supplier grouping
    """,

    'author': "Bits Americas",
    'website': "http://www.bitsamericas.com",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Operations/Purchase',
    'version': '13.0.1.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'purchase'
    ],

    # always loaded
    'data': [
        'data/ir.filters.csv'
    ],

    'installable': True,
}
