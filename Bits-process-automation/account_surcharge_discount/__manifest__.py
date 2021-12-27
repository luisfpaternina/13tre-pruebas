# -*- coding: utf-8 -*-
{
    'name': "account_surcharge_discount",
    'summary': """
        Allows to apply general discounts on sales invoices,
        You can add a fixed amount or percentage""",
    'category': 'Localization',
    'version': '13.0.1.0.0',
    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",
    'depends': [
        'sale',
        'account'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/surchange.discount.type.csv',
        'views/invoice_view.xml',
    ],
    'installable': True,
    'auto_install': True,
}
