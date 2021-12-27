# -*- coding: utf-8 -*-
{
    'name': "Freight Approval",

    'summary': """
        Module for the management of freight approval
        when they have been modified
    """,

    'author': "Bits Americas",
    'website': "http://www.bitsamericas.com",
    'category': 'Uncategorized',
    'version': '13.0.1.0.0',
    'license': 'LGPL-3',
    'depends': [
        'sale',
        'delivery'
    ],

    'data': [
        'security/security.xml',
        'views/views.xml',
    ],
}
