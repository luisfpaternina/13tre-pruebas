# -*- coding: utf-8 -*-
{
    'name': "Recruitment Appraisal Reques",

    'summary': """
        Add new model and menu
        """,

    'description': """
        new menu
    """,

    'author': "Bits Americas S.A.S",
    
    'contributors': ['Luis Felipe Paternina  luis.paternina@bitsamericas.com'],
    
    'website': "http://www.bitsamericas.com",

    'category': 'Human Resources',
    
    'version': '13.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_recruitment'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_recruitment_appraisal_request.xml',
       
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}
