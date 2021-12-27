# -*- coding: utf-8 -*-
{
    'name': "Employee Documents",

    'summary': """
        This module is to add the documents of the exam employee and others""",
    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['hr'],

    # always loaded
    'data': [
        'views/hr_employee_view.xml',
        'views/hr_employee_document_type_view.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
}
