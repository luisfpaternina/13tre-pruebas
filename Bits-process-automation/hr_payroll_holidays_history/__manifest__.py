# -*- coding: utf-8 -*-
{
    'name': "hr_payroll_holidays_history",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Uncategorized',
    'version': '13.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'hr',
        'bits_hr_payroll_news',
        'hr_payroll_approval',
        'bits_hr_payroll_news_related',
        'l10n_co_connectivity_payroll',
    ],
    # 'hr_payroll_worked_days'
    # always loaded
    'data': [
        'security/ir.model.access.csv',
#         'data/hr_payroll_holidays_data.xml',
#         'data/hr_payroll_holidays_structure.xml',
        # 'data/hr.salary.rule.csv',
        'data/hr_payroll_holidays_cron.xml',
        'views/hr_payroll_holidays_history.xml',
        'views/hr_payroll_holiday_lapse.xml',
        'views/hr_employee_holiday_menus.xml',
        'views/hr_payroll_settings.xml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': True
}
