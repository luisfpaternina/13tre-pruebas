# -*- coding: utf-8 -*-
{
    'name': "Payroll News Batch",

    'summary': """
        Provides functionality to create periodic payroll news,
        uses date range and number of periods""",
    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",
    'license': 'AGPL-3',
    'category': 'Human Resources/Payroll',
    'version': '13.0.1.0.1',
    'depends': ['base', 'bits_hr_payroll_news'],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_payroll_news_batch_cron.xml',
        'views/views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': True,
}
