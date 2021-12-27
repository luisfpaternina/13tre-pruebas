# -*- coding: utf-8 -*-
{
    'name': "Payroll paycheck",
    'summary': """
        Send mass or individually the emails with the payslip for employee""",
    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",
    'license': 'AGPL-3',
    'category': 'Human Resources/Payroll',
    'version': '13.0.1.0.1',
    'depends': [
        'base',
        'hr_payroll',
        'mail',
        'portal',
        'bits_hr_payroll_news',
    ],
    'data': [
        'views/view_payroll_paycheck.xml',
        'views/paycheck_report.xml',
        'data/mail_template_data.xml',
        'wizard/view_wizard_send_paycheck.xml',
    ],
    'installable': True,
    'auto_install': True,
}
