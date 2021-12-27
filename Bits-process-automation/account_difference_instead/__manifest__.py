# -*- coding: utf-8 -*-
{
    'name': "account_difference_instead",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Bits Americas",
    'website': "http://bitsamericas.com",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'account_asset',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_difference_instead.xml',
        'views/res_config_settings.xml',
        'data/cron.xml',
    ],
    'installable': True,
    # 'auto_install': True,
    'application': True,
    # only loaded in demonstration mode
}
