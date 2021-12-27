# -*- coding: utf-8 -*-
{
    'name': "Recruitment Profile Report",

    'summary': """
        Show information about profile recruitment in one file pdf
        """,

    'description': """
        Show information about profile recruitment in file exported to pdf
    """,

    'author': "Bits Americas S.A.S",
    'website': "http://www.bitsamericas.com",

    'category': 'Human Resources',
    'version': '13.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_recruitment', 'document_version',
                'hr_recruitment_profile_parametrization'],

    # always loaded
    'data': [
        'views/hr_job_document_version.xml',
        'views/hr_recruitment_profile_report.xml'
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}
