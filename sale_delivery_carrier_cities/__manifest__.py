# -*- coding: utf-8 -*-
{
    'name': "Sale delivery carrier cities",
    'summary': """
        Sale delivery carrier cities""",
    'author': "Bits Americas",
    'website': "http://www.bitsamericas.com",
    'category': 'Operations/Inventory',
    'version': '13.0.0.1.1',
    'depends': [
        'base',
        'delivery',
        'bits_l10n_co',
    ],
    'data': [
        'data/res.country.town.csv',
        'views/delivery_carrier_views.xml',
    ],
    'installable': True,
}
