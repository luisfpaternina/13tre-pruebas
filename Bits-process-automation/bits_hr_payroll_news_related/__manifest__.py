# -*- coding: utf-8 -*-
{
    'name': "Payroll New Related",
    'summary': """
        This module adds the news to the payroll, when the payroll is generated
        for each employee.The news is filtered by employee and by payroll
        period.""",
    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",
    'version': '13.0.1.0.0',
    # any module necessary for this one to work correctly
    'depends': [
        'bits_hr_payroll_news',
        'hr_payroll_approval'],
    # always loaded
    'data': [

    ],
    'auto_install': True,
    'installable': True,
}
