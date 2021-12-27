# -*- coding: utf-8 -*-
{
    'name': "hr_payroll_account_partner",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Module to assign res_partner to account_move and account_move_line
    """,

    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Uncategorized',
    'version': '13.0.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'account',
        'hr_payroll_account',
        'bits_hr_employee_advance',
        'hr_employee_social_security'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_salary_rule_accounts.xml',
        'views/res_config_settings_view.xml',
        'views/hr_payroll_structure_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': []
}
