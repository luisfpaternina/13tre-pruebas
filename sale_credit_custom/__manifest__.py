# -*- coding: utf-8 -*-
{
    'name': "sale_credit_custom",

    'summary': """
        Credit management module
    """,
    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com",

    'category': 'Uncategorized',
    'version': '13.0.1.0.0',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'sale_management',
        'allocation_of_credit_amount',
        'account_accountant',
    ],

    'data': [
        # 'security/ir.model.access.csv',
        'views/report_invoice.xml',
        'views/sale_order_custom_view.xml',
        'views/credit_views.xml',
        'views/bank_credit_views.xml',
        'views/invoice_views.xml',
        'wizard/sale_make_invoice_credit_custom.xml'
    ],
}
