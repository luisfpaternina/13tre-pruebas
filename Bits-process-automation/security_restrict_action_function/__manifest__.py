# -*- coding: utf-8 -*-
{
    'name': "Security Restrict Action Function",

    'summary': """This module is to grant permissions for the functions to be
    executed.""",
    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/ir_actions_restrict_views.xml'
    ],
    'installable': True,
}
