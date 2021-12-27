# -*- coding: utf-8 -*-
{
    'name': "payroll_provisions_report",

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
        'hr_payroll',
        'bits_hr_payroll_news',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/payroll_provisions_report.xml',
        'views/payroll_provisions_report_menu.xml',
        'views/res_config_settings.xml',
    ],
    'auto_install': True,
    'installable': True,
}
