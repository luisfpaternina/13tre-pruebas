# -*- coding: utf-8 -*-
{
    'name': "l10n_co_e_invoice_act_fields",
    'summary': """
        Fields available to relate electronic billing
        with technology providers""",
    'category': 'Localization',
    'version': '13.0.1.0.0',
    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",
    'depends': [
        'base',
        'account'
    ],
    'data': [
#         'data/account.act.fields.csv',
        'security/ir.model.access.csv',
        'views/account_act_fields.xml',
    ],
}
