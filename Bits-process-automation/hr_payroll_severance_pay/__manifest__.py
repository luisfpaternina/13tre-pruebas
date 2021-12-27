# -*- coding: utf-8 -*-
{
    'name': "Hr Payroll Severance Pay",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",
    'license': 'AGPL-3',
    'category': 'Human Resources/Payroll',
    'version': '13.0.1.0.1',
    'depends': [
        'base',
        'bits_hr_payroll_news',
        'hr_contract_history'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
#         'data/hr_payroll_data.xml',
        # 'data/hr.salary.rule.csv'
    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    # 'auto_install': True,
}
