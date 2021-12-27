# -*- coding: utf-8 -*-
{
    'name': "Calculate Days Worked",

    'summary': """
        This module Corrects the calculation of days worked made by odoo, such
        correction must be made because odoo does not calculate the days of the
        day as the company requires.""",
    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['hr_payroll'],

    # always loaded
    'data': [
        'views/hr_payslip_view.xml'
    ],
    'installable': True,
}
