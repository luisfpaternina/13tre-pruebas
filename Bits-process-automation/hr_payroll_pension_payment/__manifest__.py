# -*- coding: utf-8 -*-
{
    'name': "hr_payroll_pension_payment",

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
        # 'security/ir.model.access.csv',
        'views/hr_employee_pensions_contrib_view.xml',
        'views/res_config_settings.xml',
    ],
    'installable': True,
    'auto_install': True,
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
