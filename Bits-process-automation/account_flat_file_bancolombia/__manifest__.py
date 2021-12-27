# -*- coding: utf-8 -*-
{
    'name': "Account Flat File Bancolombia",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
       Fill fields and create flat file bancolombia
    """,

    'author': "Bits Americas",
    'website': "http://www.bitsamericas.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0
    # odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'account_flat_file_base',
        'account_collective_payments',
        'contacts',
        'bits_res_partner_advance',
        ],

    # always loaded
    'data': [
        'wizard/account_flat_file_bancolombia_view.xml'
    ],
    'installable': True,
}
