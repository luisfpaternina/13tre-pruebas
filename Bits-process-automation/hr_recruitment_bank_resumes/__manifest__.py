# -*- coding: utf-8 -*-
{
    'name': "hr_recruitment_bank_resumes",

    'summary': """Almacenar la información de los postulantes""",

    'description': """
        El sistema se encarga de presentar en pantalla el
        banco de hojas de vida
    """,

    'author': "Bits Americas S.A.S",
    'website': "http://www.bitsamericas.com",

    'category': 'Human Resources',
    'version': '13.0.1.0.0',

    'depends': ['hr_recruitment'],

    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
