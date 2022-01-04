# -*- coding: utf-8 -*-
{
    'name': "Campos añadidos para el funcionamiento correcto del registro de clientes",

    'summary': """""",

    'description': """
        Genera campos necesarios para el correcto funcionamiento del registro de clientes
    """,

    'author': "ProcessControl",
    'website': "http://www.processcontrol.es",
    'category': 'Revenues',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'auth_signup'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/views.xml',
    ]
    # only loaded in demonstration mode
    # 'demo': [
    # 'demo/demo.xml',
    # ],
}
