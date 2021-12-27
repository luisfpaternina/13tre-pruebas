# -*- coding: utf-8 -*-
{
    'name': "purchase_budget_revision",
    'summary': """
        Check budget when making request for quotation""",
    'author': "Bits Americas",
    'website': "http://www.bitsamericas.com",
    'category': 'Operations/Purchase',
    'version': '13.0.0.1.0',
    'depends': [
        'base',
        'purchase',
        'account_budget',
        'hr'
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'security/purchase_budget_revision_security.xml',
        'views/views.xml',
        'data/mail_template_data.xml',
    ],
    'installable': True,
}
