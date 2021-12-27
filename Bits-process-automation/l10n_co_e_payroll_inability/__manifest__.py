# -*- coding: utf-8 -*-
{
    'name': "l10n_co_e_payroll_inability",
    'summary': """
        Create model Inability to payroll""",
    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",
    'category': 'Uncategorized',
    'version': '13.0.0.0.1',
    'depends': [
        'hr_payroll',
        'bits_hr_payroll_news',
    ],
    'data': [
        'views/hr_inability_views.xml',
        'views/hr_payroll_news_views.xml',
        'security/ir.model.access.csv',
        'views/hr_inability_menu_action.xml',
        'views/hr_salary_rule_views.xml',
        'data/hr_inability_data.xml'
    ],
}
