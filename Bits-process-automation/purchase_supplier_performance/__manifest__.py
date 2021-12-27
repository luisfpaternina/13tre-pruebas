# -*- coding: utf-8 -*-
{
    'name': "Supplier Performance",

    'summary': """
        This module is to qualify suppliers once they deliver the purchased
        products.""",
    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/supplier_qualification_wizard_view.xml',
        'views/res_partner_performance_view.xml',
        'views/purchase_order_view.xml'
    ],
    'installable': True,
}
