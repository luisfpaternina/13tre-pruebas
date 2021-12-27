# -*- coding: utf-8 -*-

{
    'name': "L10n_co account currency",
    'summary': """
        Manage additional functionalities of the local
        currency for electronic Billing""",
    'author': "Bits Americas",
    'website': "http://www.bitsamericas.com",
    'category': 'Accounting/Accounting',
    'version': '13.0.1.0.0',
    'depends': [
        'base',
        'account_surcharge_discount',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/account_view.xml',
    ],
    'installable': True,
    'auto_install': True,
}
