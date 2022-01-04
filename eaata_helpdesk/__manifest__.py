# -*- coding: utf-8 -*-

{
    'name': 'Helpdesk extension for eaata',
    'version': '1.2',
    'category': 'Operations/Helpdesk',
    'summary': 'Helpdesk extension for eaata.',
    'depends': [
        'helpdesk',
        'product',
        'crm'
    ],
    'data': [
	    'security/ir.model.access.csv',
        'data/helpdesk_data.xml',
        'views/helpdesk_ticket_views.xml',
        'views/helpdesk_tool_brand_views.xml',
        'views/helpdesk_tool_model_views.xml',
        'views/helpdesk_vehicle_brand_views.xml',
        'views/helpdesk_year_views.xml',
        'views/product_views.xml',
        'views/crm_lead_views.xml',
        'views/res_partner_views.xml',
    ],

    'installable': True,
    'auto_install': False,
}
