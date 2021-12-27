# -*- coding: utf-8 -*-
{
    'name': "Depreciation Asset Collective",

    'summary': """
        This module is to carry out the process of massive depreciation of
        assets.""",
    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['account_asset', 'account_asset_intangible'],

    # always loaded
    'data': [
        'wizard/depreciation_asset_collective_view.xml'
    ],
    'installable': True,
}
