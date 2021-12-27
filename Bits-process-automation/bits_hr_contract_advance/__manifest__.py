# -*- coding: utf-8 -*-
{
    'name': "bits_hr_contract_advance",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
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
        'hr_payroll',
        'bits_hr_payroll_news'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_contract_views.xml',
        'views/hr_salary_aid.xml',
#         'data/hr_salary_aid_data.xml',
#         'data/hr.salary.rule.csv'
    ],
    'demo': [],
    'auto_install': True,
    'installable': True
}
