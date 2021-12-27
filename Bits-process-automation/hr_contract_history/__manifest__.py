# -*- coding: utf-8 -*-
{
    'name': "hr_contract_history",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",
    'version': '13.0.1.0.0',
    'depends': [
        'base',
        'hr_contract',
        'hr_payroll'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_contract_views.xml',
        'views/templates.xml',
    ],
    'installable': True,
}
