# -*- coding: utf-8 -*-
{
    'name': "l10n_co_e_payroll",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",
    'category': 'Uncategorized',
    'version': '13.0.0.0.1',
    'depends': [
        'base',
        'hr_payroll',
        'l10n_co_payroll_act_fields',
        'l10n_co_e_payroll_sequence',
        'l10n_co_tech_provider_payroll',
        'l10n_co_employee_advance_payroll',
        'bits_hr_payroll_news',
        'hr_payroll_settlement',
        'account_collective_payments'
    ],

    'data': [
        'views/hr_payslip.xml',
        'views/hr_payslip_run_views.xml',
        'views/hr_payroll_news_views.xml',
        'views/hr_salary_rule_views.xml',
        'views/payment_form_views.xml',
        'views/account_act_fields_view.xml',
        'views/res_company_views.xml',
        #'views/res_partner_views.xml',
        'views/payment_method_views.xml',
        'views/hr_payslip_dian_detail.xml',
        'data/cron.xml',
        'wizard/account_collective_payments_wizard_view.xml',
        'security/ir.model.access.csv',
        'data/decimal_precision_data.xml',
        'data/payment.method.csv',
        'data/payment.way.csv'
    ],
}
