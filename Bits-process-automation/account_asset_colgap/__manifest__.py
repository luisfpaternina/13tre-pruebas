# -*- coding: utf-8 -*-
{
    'name': "Account Asset Colgap",

    'description': """
        This module is for configuration of asset type Colgap
    """,

    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/",
    'category': 'Accounting',
    'version': '13.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['account_asset'],

    # always loaded
    'data': [
        'views/account_asset_view.xml'
    ],
    'auto_install': True,
    'installable': True,
}
