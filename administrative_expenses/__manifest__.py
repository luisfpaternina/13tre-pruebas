{
    'name': 'Administrative expenses',

    'version': '13.0.1.0',

    'author': "Nybble group",

    'contributors': ['Luis Felipe Paternina'],

    'website': "",

    'category': 'Sale',

    'depends': [

        'account_accountant',
        'sale_management',
        'sale_subscription',

    ],

    'data': [
       
        'views/account_move.xml',
        'views/sale_order.xml',
                   
    ],
    'installable': True
}
