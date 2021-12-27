# -*- coding: utf-8 -*-
{
    'name': "Ace comaderas reports",

    'summary': """
        stock picking payment""",

    'author': "Bits Americas",

    'website': "http://www.bitsamericas.com",

    'category': 'Operations/Inventory',

    'version': '13.0.0.1.3',

    'depends': [
        'stock',
        'sale_management',
        'account_accountant'
    ],

    'data': [
        "reports/invoice_report.xml"
        "reports/product_labels_report.xml"
    ],
    
    'installable': True,
}
