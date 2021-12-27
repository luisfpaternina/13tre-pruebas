# -*- coding: utf-8 -*-
{
    'name': "hr_recruitment_profile",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_employee_organization_chart'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/view_job.xml',
    ]
}
