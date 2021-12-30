# -*- coding: utf-8 -*-
{
    'name': "stock picking payment",

    'summary': """
        stock picking payment""",

    'author': "Bits Americas",

    'website': "http://www.bitsamericas.com",

    'contributors': ['Luis Felipe Paternina'],

    'category': 'Operations/Inventory',

    'version': '13.0.0.1.3',

    'depends': [
        'stock',
        'sale_management',
        'account_accountant'
    ],

    'data': [
        "views/view_stock_picking.xml"
    ],
    
    'installable': True,
}
