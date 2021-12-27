# -*- coding: utf-8 -*-
{
    'name': "Hr Employee Organization Chart",

    'summary': """
        This module orders employees by department and job.""",

    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",

    'category': 'Uncategorized',
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['hr'],

    # always loaded
    'data': [
        'views/view_job.xml',
        'views/views.xml'
    ],
}
