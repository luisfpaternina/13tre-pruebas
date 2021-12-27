# -*- coding: utf-8 -*-
{
    'name': "sale order origin city delivery",
    'summary': """
        Sale order origin city delivery""",
    'author': "Bits Americas",
    'website': "http://www.bitsamericas.com",
    'category': 'Operations/Inventory',
    'version': '13.0.0.1.3',
    'depends': [
        'sale_delivery_carrier_cities',
        'bits_res_partner_advance',
        'bits_l10n_co'
    ],
    'data': [
        'views/delivery_carrier_views.xml',
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
}
