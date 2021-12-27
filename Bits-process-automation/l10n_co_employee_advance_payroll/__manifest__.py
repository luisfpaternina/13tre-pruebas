# -*- coding: utf-8 -*-
{
    'name': "l10n_co_employee_advance_payroll",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'author': "Bits Americas",
    'website': "http://www.bitsamericas.com",
    'category': 'Accounting/Accounting',
    'version': '13.0.1.0.1',
    'depends': [
        'base',
        'hr',
        'hr_payroll',
        'bits_res_partner_advance',
    ],
    'data': [
        'views/hr_contract_employee_ne.xml',
        'views/res_config_settings.xml',
        'views/hr_contract_ne.xml',
    ],
}
