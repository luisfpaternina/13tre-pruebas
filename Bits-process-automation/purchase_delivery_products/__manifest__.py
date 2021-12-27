# -*- coding: utf-8 -*-
{
    'name': "purchase_delivery_products",

    'summary': """
       Check delivery products when making request for quotation""",

    'author': "Bits Americas",
    'website': "http://www.bitsamericas.com",

    'category': 'Operations/Purchase',
    'version': '13.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'purchase',
        'purchase_stock',
        'security_restrict_action_function',
    ],

    # always loaded
    'data': [
        'views/purchase_delivery_products_form_view.xml',
        'data/restrict_action.xml',
    ],
    'installable': True,

}
