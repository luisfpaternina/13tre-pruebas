# -*- coding: utf-8 -*-
{
    'name': "Account Analytic Required",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        In English
    """,

    'author': "Bits Americas",
    'website': "http://www.bitsamericas.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accountent',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'account',
        'account_accountant'
        ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_analityc_required_view.xml',
    ],    
    # 'auto_install': True,
    'installable': True,
}
