# -*- coding: utf-8 -*-
{
    'name': "Recruitment interview survey",

    'summary': """
        Add new funcionality
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
    'depends': ['hr_recruitment', 'survey','hr_recruitment_survey'],

    # always loaded
    'data': [
        #'security/ir.model.access.csv',
        'views/hr_applicant.xml',
        'views/hr_job.xml',
        'wizard/wizard_print_survay.xml',
        'wizard/wizard_survey.xml',
       
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}
