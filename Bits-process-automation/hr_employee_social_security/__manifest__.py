# -*- coding: utf-8 -*-
{
    'name': "hr_employee_social_security",

    'summary': """
        add different options for employee social security data.""",
    'description': """
        Se agrega la funcionalidad de crear y realizar la carga masiva de las
        entidades de seguridad social, con el objetivo de agregarle a el
        empleado la seguridad social que le corresponde
    """,
    'author': "Bits Americas.",
    'website': "https://www.bitsamericas.com/inicio",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Human Resources/ social security',
    'version': '13.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'hr',
        'hr_contract'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/social.security.csv',
        'views/social_security_view.xml',
        'views/hr_employee_social_security.xml',
        'views/hr_contract_parafsical.xml',
    ],
    'auto_install': True,
    'installable': True,
}
