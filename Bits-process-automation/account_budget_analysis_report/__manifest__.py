# -*- coding: utf-8 -*-
{
    'name': "Budget Analysis",

    'summary': """This module is used for improve budget analysis""",
    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly

    'depends': [
        'base',
        'account',
        'account_budget'],

    # always loaded
    'data': [

        'security/ir.model.access.csv',
        'views/general_budget_analysis_report_view.xml',

    ],
    'installable': True,
}
