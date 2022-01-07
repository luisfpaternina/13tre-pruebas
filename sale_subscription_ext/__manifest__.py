{
    'name': 'SAT COMPANIES',

    'version': '14.0.1',

    'author': "Process Control",

    'contributors': ['Luis Felipe Paternina'],

    'website': "https://www.processcontrol.es/",

    'category': 'Maintenance',

    'depends': [

        'sale_management',
        'contacts',
        'account_accountant',
        'account',
        'sale_subscription',
        'crm',
        'base',
        'base_automation',
        'hr_holidays'

    ],

    'data': [
       
        'security/security.xml',
        'security/ir.model.access.csv',
        #'views/account_move.xml',
        'views/res_company.xml',
        'views/account_move_line.xml',
                   
    ],
    'installable': True
}

