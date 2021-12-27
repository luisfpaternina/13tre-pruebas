# -*- coding: utf-8 -*-

{
    'name': 'L10n_co - Dian resolutions',
    'category': 'Localization',
    'version': '13.0.1.0.0',
    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",
    'summary': """
        Allows add electronic billing resolutions as Odoo sequences""",
    'depends': [
        'account',
    ],
    'data': [
        'views/ir_sequence_view.xml',
        'views/account_view.xml',
        'views/account_journal_views.xml',
    ],
    'installable': True,
}
