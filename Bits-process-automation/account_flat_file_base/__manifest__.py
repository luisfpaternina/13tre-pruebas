# -*- coding: utf-8 -*-
{
    'name': "Account Flat File Base",
    'summary': """
        This module is the basis for the bank flat file modules and more.""",
    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",
    'version': '13.0.1.0.0',
    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'account_collective_payments_supplier'],
    # always loaded
    'data': [
        'views/account_payment_view.xml',
        'views/res_partner_bank_view.xml',
        'views/account_collective_payments_supplier_view.xml',
        'wizard/account_flat_file_base_view.xml'
    ],
    'auto_install': True,
    'installable': True,
}
