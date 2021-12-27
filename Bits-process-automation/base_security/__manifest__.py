# -*- coding: utf-8 -*-
{
    'name': "Base Security",

    'summary': """
       This module is created to assign the permissions and groups required to
       enter the system, according to the established by the company.""",
    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account_accountant', 'hr_payroll',
                'account_followup', 'account_asset', 'account_budget',
                'l10n_us_reports', 'bits_hr_payroll_news',
                'account_check_printing', 'snailmail_account_followup',
                'hr_payroll_account', 'payment_transfer',
                'hr_payroll_account_partner', 'purchase_supplier_performance'],

    # always loaded
    'data': [
        "data/data_cfo.xml",
        "data/data_accountant.xml",
        "data/data_accounting_analyst.xml",
        "data/data_accounting_assistant.xml",
        "data/data_payroll_treasury.xml",
        "data/data_accounting_practitioner.xml",
        "data/data_human_talent.xml",
        "data/data_commercial.xml",
        "data/data_administrative_manager.xml",
        "data/data_permission_base.xml",
        "data/data_purchase_ accounting_assistant.xml",
        "data/data_purchase_human_talent.xml",
        "data/data_purchasing_manager.xml",
        "data/data_purchase_administrative_manager.xml",
        "data/res.groups.csv"
    ],
    'installable': True,
}
