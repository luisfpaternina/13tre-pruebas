# -*- coding: utf-8 -*-
{
    'name': "Settlement",

    'description': """
        Long description of module's purpose
    """,

    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",

    'category': 'Uncategorized',
    'version': '13.0.0.1.0',

    'depends': [
        'hr',
        'account_accountant',
        'bits_hr_payroll_news_batch',
        'hr_payroll_severance_pay',
        'bits_res_partner_advance',
        'bits_hr_contract_advance',
        'hr_payroll_holidays_history',
        'hr_contract_history'
    ],
    'data': [
        'data/account.journal.csv',
        'views/hr_payroll_report.xml',
        'views/hr_payroll_views.xml',
        'data/hr_payroll_structure_data.xml',
#         'data/hr.salary.rule.csv',
        'views/payroll_settlement_report.xml',
        'views/payroll_settlement_views.xml',
        'views/reasons_for_termination_views.xml',
        'views/res_config_settings.xml',
        'data/reasons.for.termination.csv',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
