# -*- coding: utf-8 -*-
{
    'name': "Intangible Assets",

    'description': """
        Long description of module's purpose
    """,

    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/",
    'category': 'Uncategorized',
    'version': '13.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['account_asset', 'account_accountant'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views_account_assent_intangible.xml',
    ],
    'auto_install': True,
    'installable': True,
}
