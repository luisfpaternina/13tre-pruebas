# -*- coding: utf-8 -*-
{
    'name': "account_flat_file_parafiscal",

    'summary': """
        """,

    'author': "Bits Americas",
    'website': "http://www.bitsamericas.com",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Financial area',
    'version': '13.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'account_flat_file_base',
        'account_collective_payments',
        'bits_hr_payroll_news_related',
        'hr_payroll_account',
        'bits_hr_payroll_news',
        'hr_employee_social_security',
        'bits_social_security_transfer',
        'bits_hr_employee_advance',
        'bits_res_partner_advance',
        'bits_l10n_co',
        'hr_payroll_settlement',
        'hr_contract_history',
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizard/account_parafiscal_view.xml',
        'views/templates.xml',
        'views/res_config_settings.xml',
    ],
    'auto_install': True,
    'installable': True,
}
