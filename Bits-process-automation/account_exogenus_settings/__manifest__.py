# -*- coding: utf-8 -*-
{
    'name': "Exogenus Settings",

    'summary': """This module is used for the configuration Exogenus.""",
    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly

    'depends': [
        'base',
        'account',
        'account_asset',
        'account_invoice_extract',
        'bits_res_partner_advance',
        'bits_l10n_co',
        'account_budget'],

    # always loaded
    'data': [

        'data/account.concept.exogenus.line.csv',
        'data/account.format.exogenus.csv',
        'data/account.concept.exogenus.csv',
        'security/ir.model.access.csv',
        'views/account_format_exogenus_view.xml',
        'views/account_concept_exogenus_view.xml',
        'views/account_column_configuration.xml',
        'views/account_tax.xml',
        'views/account_account.xml',
        'views/res_partner_view.xml',
        'views/account_shareholders_company.xml',
        'wizard/wizard_exogenus_print_xls.xml'

    ],
    'installable': True,
}
