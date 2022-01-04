# -*- coding: utf-8 -*-
{
    'name': "Control Pagos Pendientes",

    'summary': """""",

    'description': """
        Controla si un cliente tiene pagos pendientes cuando se confirma un pedido de venta.
    """,

    'author': "ProcessControl",
    'website': "https://www.processcontrol.es",
    'category': 'Revenues',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale_management','account'],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        'wizard/alert_wizard.xml',
        'views/views.xml',
    ]
    # only loaded in demonstration mode
    #'demo': [
        #'demo/demo.xml',
    #],
}