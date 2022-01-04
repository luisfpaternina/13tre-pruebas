# -*- coding: utf-8 -*-
{
    "name": "Limited Access for Products",
    "version": "13.0.1.0.2",
    "category": "Sales",
    "author": "faOtools",
    "website": "https://faotools.com/apps/13.0/limited-access-for-products-438",
    "license": "Other proprietary",
    "application": True,
    "installable": True,
    "auto_install": False,
    "depends": [
        "product"
    ],
    "data": [
        "data/data.xml",
        "security/ir.model.access.csv",
        "security/security.xml"
    ],
    "qweb": [
        "static/src/xml/message_edit.xml"
    ],
    "js": [
        
    ],
    "demo": [
        
    ],
    "external_dependencies": {},
    "summary": "The tool to restrict rights for create, edit and delete products",
    "description": """
For the full details look at static/description/index.html

* Features * 
- Product readonly rights
- Rights for product configuration documents
- Limited access for product interfaces



#odootools_proprietary

    """,
    "images": [
        "static/description/main.png"
    ],
    "price": "28.0",
    "currency": "EUR",
    "live_test_url": "https://faotools.com/my/tickets/newticket?&url_app_id=29&ticket_version=13.0&url_type_id=3",
}