# -*- coding: utf-8 -*-

{
    'name': 'L10n_co - subsidy connectivity',
    'category': 'Localization',
    'version': '13.0.1.0.0',
    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",
    'summary': """
        Allows add the subsidy's connectivity""",
    'depends': [
        'base',
        'hr_payroll',
        'hr_connectivity_sub',
        'bits_hr_payroll_news',
    ],
    'data': [
        'views/connectivity_payroll_e_view.xml',
        'views/l10n_co_hr_payroll_rule.xml',
        'views/hr_contract_teleworker.xml',
    ],
    'installable': True,
}
