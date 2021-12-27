# -*- coding: utf-8 -*-
{
    'name': "stock_picking_report_description",

    'summary': """
        Some fields was changed in the report""",

    'description': """
        Change product field by description field and It was added note
        to report
    """,

    'author': "Bits Americas S.A.S.",
    'website': "http://www.bitsamericas.com",

    'category': 'Invoicing',
    'version': '13.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['stock', 'purchase'],

    # always loaded
    'data': [
        'report/stock_picking_inherit.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
