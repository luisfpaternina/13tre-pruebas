# -*- coding: utf-8 -*-
{
    'name': "account_trial_balance_report_advance",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Uncategorized',
    'version': 'v13.0.1.0.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'account_account_level', 'web', 'account_reports',
        'account_account_fiscal', 'account_difference_report_niif_colgap'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_trial_balance_report_advance_templates.xml',
        'views/report_financial.xml'
    ],
}
