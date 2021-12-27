# -*- coding: utf-8 -*-
{
    'name': "account_accounting_closing_settings",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Bits Americas S.A.S.",
    'website': "http://www.bitsamericas.com",

    'category': 'Uncategorized',
    'version': '13.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_accountant'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_fiscal_year_inherit_form.xml',
        'views/account_account_inherit_form.xml'
    ]
}
