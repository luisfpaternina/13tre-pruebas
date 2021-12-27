# -*- coding: utf-8 -*-
{
    'name': "payroll_holidays_report",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Module created for the settlement of
        vacations without being linked to the
        settlement of the payroll
    """,

    'author': "Bits Americas S.A.S.",
    'website': "https://www.bitsamericas.com/",
    'version': '13.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'hr_payroll_paycheck',
        'bits_hr_payroll_news',
        'hr_payroll_holidays_history',
        'bits_hr_payroll_news_related'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/view_payroll_holidays.xml',
        'views/templates.xml',
        'views/payroll_holidays_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto_install': True,
}
