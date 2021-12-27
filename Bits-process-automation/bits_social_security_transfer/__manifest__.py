# -*- coding: utf-8 -*-
{
    'name': "bits_social_security_transfer",
    'summary': """
        Module to take control of the change
        of Social Security entities""",
    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",
    'category': 'Human Resources/ social security',
    'version': '13.0.0.1.0',
    'depends': [
        'base',
        'hr_employee_social_security'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/social_security_transfer_view.xml',
        'views/templates.xml',
    ],
    'installable': True,
}
