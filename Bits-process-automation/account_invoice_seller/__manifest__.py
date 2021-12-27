# -*- coding: utf-8 -*-
{
    'name': "account_invoice_seller",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Bits Americas S.A.S.",
    'website': "http://www.bitsamericas.com",

    'category': 'Invoicing',
    'version': '13.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'account_asset', 'account_accountant'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
