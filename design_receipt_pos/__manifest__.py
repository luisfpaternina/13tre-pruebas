# -*- coding: utf-8 -*-
{
    'name': "Design receipt pos",
    'summary': """
        Design receipt pos""",
    'author': "Bits Americas",
    'website': "http://www.bitsamericas.com",
    'category': 'Operations/Inventory',
    'version': '13.0.0.1.2',
    'depends': [
        'bits_res_partner_advance',
        'l10n_co_pos',
        'point_of_sale',
    ],
    'data': [
        'views/assets.xml',
        'views/pos_config_views.xml'
    ],
    'qweb': ['static/src/xml/pos.xml'],
    'installable': True,
}
