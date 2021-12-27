# -*- coding: utf-8 -*-
{
    'name': "account_payment_flow",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Bits Americas S.A.S",
    'website': "https://bitsamericas.com",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Accounting',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'contacts',
        'account',
        'mail',
        'rating',
        'purchase'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_move_views.xml',
        'views/account_payment_flow.xml',
        'views/account_payment_flow_menus.xml',
        'views/account_payment_flow_stage.xml',
        'views/account_payment_flow_stage_menus.xml',
        'views/account_payment_flow_stage_team.xml',
        'data/account_payment_flow_stage_data.xml',
        'data/account_payment_method.xml',
        'data/account_payment_flow_mail_data.xml'
    ],
    'demo': [],
}
