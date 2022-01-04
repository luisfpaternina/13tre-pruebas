# -*- coding: utf-8 -*-
{
    'name': "Calculadora de comerciales intermedios para clientes",

    'summary': """""",

    'description': """
        Este modulo nos genera la posibilidad de marcar usuarios de portal como intermediario. Posteriomente, nos 
        permite obtener informe de comisiones sobre las facturas de sus clientes en base a un % establecido
        en la ficha de cliente
    """,

    'author': "ProcessControl",
    'website': "http://www.processcontrol.es",
    'category': 'Alerts',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale_management','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
    ]
    # only loaded in demonstration mode
    #'demo': [
        #'demo/demo.xml',
    #],
}