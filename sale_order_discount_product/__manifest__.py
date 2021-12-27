# -*- coding: utf-8 -*-
{
    'name': "sale_order_discount_product",

    'summary': """
        This module will allow the validations
        for the discount in a sales order
    """,

    'description': """
        This module will allow the different
        validations for the discount in a
        sales budget, taking into account
        the different models
    """,

    'author': "Bits Americas S.A.S",
    'website': "http://www.bitsamericas.com",

    'category': 'Uncategorized',
    'version': '13.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'product',
        'freight_approval',
    ],

    # always loaded
    'data': [
        'data/data_discount_table.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/res_config_settings_view.xml',
        'views/discount_table_view.xml',
        'views/product_category_view.xml',
        'views/quotation_view.xml',
    ],
    'post_init_hook': '_post_init_hook_sale_order_discount_product',
    'uninstall_hook': "uninstall_hook",
}
