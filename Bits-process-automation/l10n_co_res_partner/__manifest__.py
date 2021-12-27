# -*- coding: utf-8 -*-
{
    'name': 'l10n_co Partners',
    'summary': """
        Adds functionalities related to the Colombian localization""",
    'category': 'Localization',
    'version': '13.0.1.0.0',
    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",
    'depends': [
        'base',
        'contacts',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/l10n_co_res_partner.xml',
        'views/ciiu.xml',
        'data/ciiu.csv',
    ],
    'installable': True,
    'auto_install': True,
}
