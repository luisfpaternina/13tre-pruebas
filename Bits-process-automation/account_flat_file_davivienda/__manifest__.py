# -*- coding: utf-8 -*-
{
    'name': "account_flat_file_davivienda",

    'summary': """
        Add functionality to upload Davivienda Flat File
    """,

    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'bits_res_partner_advance',
        'bits_hr_employee_advance',
        'account_flat_file_base',
        'account_collective_payments',
    ],

    # always loaded
    'data': [
        'wizard/account_flat_file_davivienda.xml',
    ],
    'auto_install': True,
    'installable': True,
}
