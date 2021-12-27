# -*- coding: utf-8 -*-
{
    'name': "hr_recruitment_postulation",

    'summary': """
        Extended hr applicant for field identities
        Identification Number, Internal Request""",

    'description': """
        Extended functionality to hr applicant
        Identification number and Internal request link to web form
    """,

    'author': "BitsAmericas S.A.S",
    'website': "http://www.bitsamericas.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base
    # /data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'website_hr_recruitment',
        'hr_employee_internal_request',
        'hr_recruitment_bank_resumes'
    ],

    # always loaded
    'data': [
        'views/templates.xml',
        'views/hr_applicant_inherit_view.xml',
        'views/hr_applicant_inherit_search.xml',
        'views/hr_employee_internal_request_inherit_view.xml',
        'security/security.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
