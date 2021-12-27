# -*- coding: utf-8 -*-
{
    'name': "allocation_of_credit_amount",

    'summary': """
        Module for credit allocation management
    """,

    'author': "Bits Americas",
    'website': "http://www.bitsamericas.com",
    'category': 'Uncategorized',
    'version': '13.0.1.2.0',
    'license': 'LGPL-3',
    'depends': [
        'sale_management',
        'contacts',
        'bits_res_partner_advance',
        'account_followup',
    ],

    'data': [
        'data/account_journal_data.xml',
        'data/product_data.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/credit_types_views.xml',
        'views/credit_views.xml',
        'views/res_partner.xml',
        'data/cron_check_credit_status.xml',
    ],
}
