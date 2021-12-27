# -*- coding: utf-8 -*-
{
    'name': "bits_account_move_validation_analytic",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'author': "Bits Americas",
    'website': "http://www.bitsamericas.com",
    'category': 'Accounting/Accounting',
    'version': '13.0.1.0.1',
    'depends': [
        'base',
        'account_asset',
        'account_accountant'
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_config_settings.xml',
        'views/templates.xml',
    ],
}
