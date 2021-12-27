# -*- coding: utf-8 -*-
{
    'name': "purchase_supplier_approval",

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
        'hr',
        'purchase',
        'bits_hr_contract_advance',
        'security_restrict_action_function'
    ],
    # always loaded
    'data': [
        'data/action_restrict.xml',
        'data/mail_template_approved.xml',
        'views/purchase_order.xml',
        'views/templates.xml'
    ],
    # only loaded in demonstration mode
    'demo': [],
}
