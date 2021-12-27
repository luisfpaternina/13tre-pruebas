# -*- coding: utf-8 -*-
{
    'name': "Payroll Flat File Parafiscal",

    'summary': """
        This module calculates the retention of each of the employees.""",
    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['account_flat_file_parafiscal'],

    # always loaded
    'data': [
        'wizard/hr_payroll_flat_file_parafiscal_view.xml'
    ],
    'installable': True,
}
