# -*- coding: utf-8 -*-
{
    'name': "EAATA Subscription",

    'summary': """
        EAATA Subscription
    """,

    'description': """
        EAATA Subscription
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
        'sale_subscription'
    ],

    # always loaded
    'data': [
	    'security/ir.model.access.csv',
        'views/sale_subscription_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],

}
