# -*- coding: utf-8 -*-
{
    'name': "account_provision_deteriorate_receivable_settings",

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
    'depends': [
        'base',
        'account',],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_provision_deteriorate_receivable_settings_view.xml',
    ],
}
