# -*- coding: utf-8 -*-
{
    'name': "Payroll Employee Retention",

    'summary': """
        This module calculates the retention of each of the employees.""",
    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_payroll', 'bits_hr_payroll_news',
                'bits_hr_contract_advance', 'hr_employee_document',
                'hr_payroll_holidays_history', 'hr_payroll_settlement'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'data/hr.payroll.retention.csv',
        'views/hr_payroll_parameter_retention_view.xml',
        'views/hr_payroll_retention_view.xml',
        'views/hr_payroll_settings_view.xml',
        'views/hr_payroll_uvt_range_view.xml',
        'security/ir.model.access.csv',
        'views/hr_payroll_employee_retention_view.xml',
#         'data/hr_payroll_data.xml',
#         'data/hr.payroll.parameter.retention.csv',
        # 'data/hr.salary.rule.csv',
        'data/cron.xml',
#         'data/hr.payroll.uvt.range.csv',
    ],
    'installable': True,
}
