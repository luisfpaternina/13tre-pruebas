# -*- coding: utf-8 -*-
{
    'name': "l10n_co_payroll_act_fields",
    'summary': """
        Fields available to relate electronic billing
        with technology providers""",
    'category': 'Localization',
    'version': '13.0.0.0.2',
    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",
    'depends': [
        'base',
        'hr_payroll',
        'l10n_co_account_e_invoice',
        'l10n_co_e_invoice_act_fields',
    ],
    'data': [
        'data/account.act.fields.csv',
        # 'security/ir.model.access.csv',
        'views/payroll_act_fields.xml',
    ],
}
