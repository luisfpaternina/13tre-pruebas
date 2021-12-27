# pylint: disable=locally-disabled, manifest-required-author
{
    'name': "Bits HR Payroll News",

    'summary': """
        Add the different payroll news per employee and for
        concepts related to the contract.""",
    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",
    'license': 'AGPL-3',
    'category': 'Human Resources/Payroll',
    'version': '13.0.1.0.1',
    'depends': [
        'base',
        'hr_payroll',
        'analytic',
        'base_setup',
        'mail',
        'portal',
        'rating',
        'resource'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_payroll_news_views.xml',
        'views/hr_payroll_news_stage_views.xml',
        'views/hr_salary_rule_views.xml',
        'views/hr_payslip.xml',
        'data/hr_payroll_news_stage_data.xml',
#         'data/hr_payroll_data.xml',
        'data/hr_payroll_structure_data.xml',
        #'data/hr.salary.rule.csv',
        'views/hr_payroll_news_settings.xml',
        'wizard/view_hr_payroll_news_employees.xml',
        'views/decimal_precision_views.xml',
        'views/hr_payroll_setting.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'installable': True,
    'auto_install': True,
    'application': True,
}
