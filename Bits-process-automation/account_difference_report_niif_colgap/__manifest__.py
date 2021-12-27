# -*- coding: utf-8 -*-
{
    'name': "Account Difference Report NIIF-Colgap",

    'description': """
        The purpose of the module is to create a report to see the IFRS
        differences - Colgap
    """,

    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/",
    'category': 'Accounting',
    'version': '13.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['web', 'account_reports', 'account_journal_niif'],

    # always loaded
    'data': [
        'views/difference_niif_colgap_template.xml',
        'views/search_template_view.xml',
    ],
    'auto_install': True,
    'installable': True,
}
