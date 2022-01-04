# -*- coding: utf-8 -*-
{
    'name': "Calculadora de riesgo para clientes",

    'summary': """""",

    'description': """
        Genera el campo Riesgo Disponible y Riesgo Concedido. Muestra el riesgo disponible basandose en pedidos/facturacion del cliente
    """,

    'author': "ProcessControl",
    'website': "http://www.processcontrol.es",
    'category': 'Alerts',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_management', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizard/alert_wizard.xml',
        'views/views.xml',
    ]
    # only loaded in demonstration mode
    # 'demo': [
    # 'demo/demo.xml',
    # ],
}
