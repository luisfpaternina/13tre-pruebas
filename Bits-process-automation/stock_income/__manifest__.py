# -*- coding: utf-8 -*-
{
    'name': "stock_income",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/",

    'category': 'Uncategorized',
    'version': '13.0.0.1.0',

    'depends': [
        'base',
        'stock',
        'mail',
        'portal',
    ],

    'data': [
        'data/mail_template_data.xml',
        'views/stock_income_views.xml',
        'wizard/view_wizard_send_confirmation_to_suppliers.xml',
    ],
    'installable': True,
}
