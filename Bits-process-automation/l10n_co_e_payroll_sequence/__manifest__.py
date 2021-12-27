# -*- coding: utf-8 -*-
{
    'name': "l10n_co_e_payroll_sequence",
    'summary': """
        Fields available to relate electronic billing
        with technology providers""",
    'category': 'Localization',
    'version': '13.0.1.0.0',
    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",
    'depends': [
        'base',
        'hr_payroll',
    ],
    'data': [
        'views/ir_sequence_menu_action.xml',
        'views/hr_payslip_view.xml',
        'views/hr_payroll_structure_view.xml',
    ],
}
