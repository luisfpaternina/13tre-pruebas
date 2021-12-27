# -*- coding: utf-8 -*-
{
    'name': "account_asset_niif",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_asset_colgap'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizard/asset_sell_views.xml',
    ]
}
