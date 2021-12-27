# -*- coding: utf-8 -*-
{
    'name': "Recruitment Profile Survey",

    'summary': """
        Add new funcionality in applicants
        """,

    'description': """
        Show the surveys
    """,

    'author': "Bits Americas S.A.S",
    
    'contributors': ['Luis Felipe Paternina  luis.paternina@bitsamericas.com'],
    
    'website': "http://www.bitsamericas.com",

    'category': 'Human Resources',
    
    'version': '13.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_recruitment', 'survey'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_recruitment_internal_request.xml',
        #'views/hr_recruitment_profile_report.xml'
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}
