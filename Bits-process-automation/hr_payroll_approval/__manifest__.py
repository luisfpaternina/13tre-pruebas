# -*- coding: utf-8 -*-
{
    'name': "Payroll Approval",

    'description': """
        Module used for the payroll approval process by financial executives
    """,

    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",

    'category': 'Uncategorized',
    'version': '13.0.0.1.0',

    'depends': ['base', 'hr_payroll_paycheck', 'mail', 'portal',
                'security_restrict_action_function'],

    'data': [
        'wizard/view_wizard_send_payroll_approval.xml',
        'data/mail_template_data.xml',
        'data/actions_restrict.xml',
        'views/views_hr_payroll_approval.xml',
        'views/view_hr_payroll_approval_setting.xml',
    ],
    'auto_install': True,
    'installable': True,
}
