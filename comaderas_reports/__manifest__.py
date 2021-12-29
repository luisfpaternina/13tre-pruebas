# -*- coding: utf-8 -*-
{
    'name': "Acecomaderas reports",

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

        "views/res_company.xml",
        "reports/paper_format.xml",
        "reports/invoice_report.xml",
        "reports/product_labels_report.xml",
        "reports/sale_order_report.xml",
        "reports/purchase_order_report.xml",

    ],
    
    'installable': True,
}
