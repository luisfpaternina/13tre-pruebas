# -*- coding: utf-8 -*-
{
    'name': "bits_l10n_co",

    'summary': """
        This module is used to set divipol and dian code through contacts
        module Only for Colombia""",
    'description': """
        Here we can set data related to DIAN and DIVIPOL codes,
        Too we have views in the contacts module
    """,

    'author': "BitsAmericas",
    'website': "http://www.bitsamericas.com",
    'category': 'Uncategorized',
    'version': '13.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'hr',
        'contacts'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/res.country.state.csv',
        'data/res.country.town.csv',
        'data/res.country.csv',
        # 'views/l10n_view.xml',
        'views/res_country_state_views.xml',
        'views/res_partner_views.xml',
        # 'views/hr_employee_views.xml',
    ],
}
