# -*- coding: utf-8 -*-
{
    'name': "Contacts Advance",

    'summary': """
        This module adds the type of document and the document
        number for the partners, this because Bits americas requires
        it in this way, in addition the respective validations are made
        to have a good integrity of the data.""",
    'author': "Bits Americas",
    'website': "https://www.bitsamericas.com/inicio",
    'version': '13.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': [
        'l10n_co',
        'contacts'
    ],

    # always loaded
    'data': [
        'views/views.xml',
    ],
    'auto_install': True,
    'installable': True,
}
