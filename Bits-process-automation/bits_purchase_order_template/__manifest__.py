# -*- coding: utf-8 -*-
{
    'name': "bits_purchase_order_template",
    'summary': """
        Check budget when making request for quotation""",
    'author': "Bits Americas",
    'website': "http://www.bitsamericas.com",
    'category': 'Operations/Purchase',
    'version': '13.0.0.1.0',
    'depends': [
        'base',
        'purchase'
    ],
    'data': [
        'security/ir.model.access.csv',
        'report/purchase_reports.xml',
        'data/mail_template_data.xml',
        'report/purchase_order_templates.xml'
    ],
    'installable': True,
    'auto_install': False,
}
