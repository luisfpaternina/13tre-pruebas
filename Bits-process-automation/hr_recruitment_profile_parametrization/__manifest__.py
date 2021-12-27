# -*- coding: utf-8 -*-
{
    'name': "hr_recruitment_profile_parametrization",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Bits Americas S.A.S",
    'website': "http://www.bitsamericas.com",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Human Resources',
    'version': '13.0.1.1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'hr_employee_organization_chart',
        'base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_job_view.xml',
        'views/hr_recruitment_level_menus.xml',
        'views/hr_recruitment_level.xml',
        'views/hr_recruitment_experience_menus.xml',
        'views/hr_recruitment_experience.xml',
        'views/hr_recruitment_specific_competencies.xml',
        'views/hr_recruitment_specific_competencies_menus.xml',
        'views/hr_recruitment_responsabilities_charge.xml',
        'views/hr_recruitment_responsabilities_charge_menus.xml',
        'views/hr_recruitment_organizational_competencies.xml',
        'views/hr_recruitment_organizational_competencies_menus.xml',
        'views/hr_recruitment_positions_in_charge_competencies.xml',
        'views/hr_recruitment_positions_in_charge_competencies_menus.xml',
        'views/hr_recruitment_technical_technological_competencies.xml',
        'views/hr_recruitment_technical_technological_competencies_menus.xml',
        'views/hr_recruitment_work_conditions.xml',
        'views/hr_recruitment_work_conditions_menus.xml',
    ]
}
