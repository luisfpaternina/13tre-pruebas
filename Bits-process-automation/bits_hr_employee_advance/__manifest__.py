# -*- coding: utf-8 -*-
{
    'name': "bits_hr_employee_advance",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Se extienden funcionalidad de empleado, proceso de rh bitsAmericas
    """,

    'author': "Bits Americas",
    'website': "http://www.bitsamericas.com",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'hr',
        'analytic',
        'hr_employee_social_security',
        'account_accountant'
    ],

    # always loaded
    'data': [
        'views/hr_employee_settings.xml',
        'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
        'views/hr_employee_center_cost.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'auto_install': True,
    'installable': True
}
