# -*- coding: utf-8 -*-
{
    'name': "POS Sale Order Customer",

    'summary': """
        Module where invoice records are added.
    """,

    'description': """
        Module where all the invoices that are in the 'post' state are
         listed, of which one is selected to add those
         products in the POS
    """,

    'author': "Bits Americas S.A.S.",
    'website': "http://www.bitsamericas.com",

    'category': 'Uncategorized',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        "bi_pos_import_sale"
    ],

    # always loaded
    'data': [
        "views/pos_assets.xml",
        # 'views/pos_order.xml',
        # 'views/sale_order.xml',
    ],
    "qweb": ["static/src/xml/pos.xml"],
    "installable": True,
}
