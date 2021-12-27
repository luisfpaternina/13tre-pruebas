# -*- coding: utf-8 -*-
{
    'name': "hr_employee_internal_request",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Bitsamericas",
    'website': "http://www.Bitsamericas.com",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'hr_recruitment',
        'website_hr_recruitment',
        'security_restrict_action_function',
        'hr_recruitment_appraisal_request',
        'hr_recruitment_score_profile',
        'analytic',
        'base_automation'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/hr_employee_internal_request_data.xml',
        'data/hr_employee_internal_request_sent_email_data.xml',
        'data/action_restrict.xml',
        'views/hr_employee_internal_request.xml',
        'views/hr_employee_internal_request_menus.xml',
        'views/hr_employee_internal_request_stages.xml',
        'views/hr_employee_internal_request_menus_stages.xml',
        'views/hr_job_views.xml',
        'views/hr_employee_internal_request_wizard.xml',
        'views/base_automatization.xml'
    ]
}
