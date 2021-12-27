# -*- coding: utf-8 -*-
{
    'name': "account_collective_payments_supplier",

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
        'account_collective_payments',
        'l10n_co_e_payroll'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account_collective_payments_supplier_view.xml',
        'views/account_collective_payments_supplier_menu.xml',
        'wizard/account_collective_payments_view.xml',
    ],
}
