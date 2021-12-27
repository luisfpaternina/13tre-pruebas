# -*- coding: utf-8 -*-
{
    'name': "account_collective_payments",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",
    'license': 'AGPL-3',
    'category': 'Accounting/Accounting',
    'version': '0.1',
    'depends': [
        'base',
        'l10n_co',
        'hr_payroll',
        'account_accountant',
        'account_asset',
    ],
    'data': [
        'data/payment_method_data.xml',
        'wizard/account_collective_payments_view.xml',
        'views/views.xml',
    ],
    'demo': [],
    'installable': True,
    # 'auto_install': True,
    'application': True,
}
