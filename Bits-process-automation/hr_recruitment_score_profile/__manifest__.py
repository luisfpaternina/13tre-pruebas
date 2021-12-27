{
    'name': 'hr recruitment score profile',

    "summary": """new models,fields,views""",

    'version': '13.0.1.0',

    'author': "Bits americas",
    
    'contributors': ['Luis Felipe Paternina  luis.paternina@bitsamericas.com'],

    'website': "www.bitsamericas.com",

    'category': 'rrhh',

    'depends': [

        'base',
        'hr_recruitment',

    ],

    'data': [

        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_recruitment_score_profile_view.xml',
        'views/hr_recruitment_score_skills_view.xml',
        'views/hr_recruitment_score_technologies_view.xml',
        'views/hr_recruitment_score_test_result_view.xml',
        'views/inherit_hr_applicant_view.xml',
                 
    ],
    
    "application": False,
    "installable": True,
    "auto_install": False,

}
