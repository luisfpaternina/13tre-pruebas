# -*- coding: utf-8 -*-
{
    'name': "EAATA API",

    'summary': """
        EAATA API
    """,

    'description': """
        EAATA API
    """,

    'author': "CIEL IT S/A",
    'website': "https://www.ciel-it.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',
    'application': True,

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'helpdesk',
        'crm',
        'eaata_subscription'
    ],

    # always loaded
    'data': [
    ],
    # only loaded in demonstration mode
    'demo': [
    ],

}
