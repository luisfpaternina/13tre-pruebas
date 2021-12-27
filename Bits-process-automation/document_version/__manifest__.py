# -*- coding: utf-8 -*-
{
    'name': "Document Version",
    'summary': """
        This module is for configuration version document SIGB""",
    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",
    'version': '13.0.1.0.0',
    # any module necessary for this one to work correctly
    'depends': ['base'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/document_version_view.xml'
    ],

    'installable': True,
}
